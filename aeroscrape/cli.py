"""
Command-Line Interface for AeroScrape Flight Engine.
Provides rich colored table formatting, Shabbos compliance alerts, and Kosher meal guides.
"""
import argparse
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich import box

from aeroscrape.models import (
    FlightQuery,
    CabinClass,
    ShabbosComplianceLevel,
)
from aeroscrape.scrapers.engine import AeroScrapeEngine
from aeroscrape.analytics.price_analyzer import analyze_price_trend
from aeroscrape.airports import get_airport


console = Console()


def display_results(query: FlightQuery, flights, stats, trend):
    """
    Render flight results in a rich terminal table with color-coded Shabbos and Kosher badges.
    """
    origin_info = get_airport(query.origin)
    dest_info = get_airport(query.destination)

    # Header Panel
    console.print(Panel(
        f"[bold cyan]AeroScrape Flight Price Engine[/bold cyan] - Searching [bold yellow]{origin_info.city} ({query.origin})[/bold yellow] → [bold yellow]{dest_info.city} ({query.destination})[/bold yellow]\n"
        f"Date: [green]{query.departure_date}[/green] | Passengers: [green]{query.passengers}[/green] | Cabin: [green]{query.cabin_class.value.title()}[/green]\n"
        f"Shabbos Buffer: [magenta]{query.shabbos_buffer_hours} hrs[/magenta] | Filter Violations: [magenta]{query.filter_shabbos_violations}[/magenta] | Require KSML: [magenta]{query.require_ksml}[/magenta]",
        title="Search Query Summary",
        border_style="cyan"
    ))

    if not flights:
        console.print("[bold red]No flights found matching your criteria.[/bold red]")
        if query.filter_shabbos_violations:
            console.print("[yellow]Tip: You have Shabbos violation filtering enabled. Flights arriving after Candle Lighting or departing before Havdalah were hidden.[/yellow]")
        return

    # Stats Panel
    stats_text = (
        f"Found [bold green]{stats.total_found}[/bold green] options across [cyan]{', '.join(stats.scrapers_queried)}[/cyan] in [bold]{stats.execution_time_ms} ms[/bold]\n"
        f"Cheapest Fare: [bold green]${stats.cheapest_price:.2f}[/bold green] | Average Fare: [yellow]${stats.average_price:.2f}[/yellow] | Fastest Duration: [blue]{stats.fastest_duration_minutes // 60}h {stats.fastest_duration_minutes % 60}m[/blue]\n"
        f"Shabbos-Safe Options: [bold green]{stats.shabbos_safe_count}[/bold green] | Kosher Meals Available: [bold green]{stats.kosher_available_count}[/bold green]"
    )
    console.print(Panel(stats_text, title="Meta-Scraper Summary", border_style="green"))

    # Price Trend Panel
    trend_color = "green" if "Great" in trend.price_verdict else ("yellow" if "Fair" in trend.price_verdict else "red")
    trend_text = (
        f"Verdict: [bold {trend_color}]{trend.price_verdict}[/bold {trend_color}] - {trend.verdict_summary}\n"
        f"Benchmark Normal Price: [bold]${trend.benchmark_price:.2f}[/bold] | Best Alternative Date: [bold green]{trend.recommended_date}[/bold green] (Save [bold green]${trend.potential_savings:.2f}[/bold green])"
    )
    console.print(Panel(trend_text, title="7-Day Price Analysis & Date Flexibility", border_style=trend_color))

    # Flights Table
    table = Table(
        title="Available Flight Fares (Sorted by Price)",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True
    )

    table.add_column("#", style="dim", width=3)
    table.add_column("Airline", style="bold white", width=16)
    table.add_column("Flight / Schedule", style="white", width=22)
    table.add_column("Stops & Duration", style="cyan", width=15)
    table.add_column("Total Fare", style="bold green", justify="right", width=12)
    table.add_column("Shabbos Alert Status", width=26)
    table.add_column("Kosher Meal (KSML)", width=24)
    table.add_column("Value Score & Tags", width=20)

    for idx, fl in enumerate(flights, 1):
        leg = fl.outbound_leg
        dep_str = leg.departure_time.strftime("%a, %b %d at %H:%M")
        arr_str = leg.arrival_time.strftime("%H:%M (+1)" if leg.arrival_time.date() > leg.departure_time.date() else "%H:%M")
        
        sched_text = f"{dep_str} → {arr_str}\n[dim]{leg.origin} to {leg.destination} ({leg.aircraft})[/dim]"

        stops_text = "Non-stop" if leg.stops == 0 else f"{leg.stops} Stop ({', '.join(leg.stop_airports)})"
        dur_text = f"{leg.duration_minutes // 60}h {leg.duration_minutes % 60}m\n[dim]{stops_text}[/dim]"

        price_text = f"[bold green]${fl.price.total_price:.2f}[/bold green]\n[dim]Base: ${fl.price.base_fare:.2f}[/dim]"

        # Shabbos Status Column
        sh = fl.shabbos_status
        if sh:
            if sh.level == ShabbosComplianceLevel.SAFE:
                sh_style = "[bold green]✔ SAFE[/bold green]"
            elif sh.level == ShabbosComplianceLevel.WARNING:
                sh_style = "[bold yellow]⚠ TIGHT BUFFER[/bold yellow]"
            else:
                sh_style = "[bold red]⚠️ NOT RECOMMENDED[/bold red]"
            sh_desc = sh.summary
            sh_text = f"{sh_style}\n[dim]{sh_desc}[/dim]"
        else:
            sh_text = "[dim]N/A[/dim]"

        # Kosher Status Column
        ko = fl.kosher_info
        if ko:
            if ko.mehadrin_skml_offered:
                ko_style = "[bold green]★ MEHADRIN SKML[/bold green]"
                ko_desc = f"{ko.advance_notice_hours}h notice ({ko.certification.split('/')[0]})"
            elif ko.ksml_offered:
                ko_style = "[green]✔ KSML OFFERED[/green]"
                ko_desc = f"{ko.advance_notice_hours}h notice ({ko.certification.split('/')[0]})"
            else:
                ko_style = "[bold yellow]⚠️ NO KOSHER MEAL[/bold yellow]"
                ko_desc = "Bring Kosher food with you!"
            ko_text = f"{ko_style}\n[dim]{ko_desc}[/dim]"
        else:
            ko_text = "[dim]N/A[/dim]"

        # Value Score & Tags Column
        val_text = f"[bold yellow]Score: {fl.value_score}/100[/bold yellow]\n[cyan]{', '.join(fl.tags)}[/cyan]"

        table.add_row(
            str(idx),
            f"{leg.airline_name}\n[dim]{fl.scraper_source}[/dim]",
            sched_text,
            dur_text,
            price_text,
            sh_text,
            ko_text,
            val_text
        )

    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="AeroScrape Flight Price Engine with Shabbos & Kosher Compliance")
    parser.add_argument("--origin", "-o", default="JFK", help="3-letter origin IATA code (e.g. JFK, EWR, LAX, LHR)")
    parser.add_argument("--dest", "-d", default="TLV", help="3-letter destination IATA code (e.g. TLV, LHR, FRA, CDG)")
    parser.add_argument("--date", default="2026-08-14", help="Departure date in YYYY-MM-DD format")
    parser.add_argument("--passengers", "-p", type=int, default=1, help="Number of adult passengers")
    parser.add_argument("--cabin", "-c", default="economy", choices=["economy", "premium_economy", "business", "first"])
    parser.add_argument("--shabbos-buffer", type=float, default=3.0, help="Hours of safety buffer before Candle Lighting")
    parser.add_argument("--hide-violations", action="store_true", help="Hide flights that are not recommended for Shabbos")
    parser.add_argument("--require-ksml", action="store_true", help="Only show airlines that offer Kosher meals (KSML)")
    parser.add_argument("--max-stops", type=int, default=None, help="Maximum number of stops")
    parser.add_argument("--live", action="store_true", help="Run with real live Google Flights (SerpApi) or Amadeus APIs")

    args = parser.parse_args()

    query = FlightQuery(
        origin=args.origin,
        destination=args.dest,
        departure_date=args.date,
        passengers=args.passengers,
        cabin_class=CabinClass(args.cabin),
        shabbos_buffer_hours=args.shabbos_buffer,
        filter_shabbos_violations=args.hide_violations,
        require_ksml=args.require_ksml,
        max_stops=args.max_stops
    )

    if args.live:
        import os
        from aeroscrape.scrapers.live_adapter import SerpApiGoogleFlightsScraper, AmadeusLiveScraper
        live_scrapers = []
        if os.getenv("SERPAPI_KEY"):
            live_scrapers.append(SerpApiGoogleFlightsScraper())
        if os.getenv("AMADEUS_CLIENT_ID") and os.getenv("AMADEUS_CLIENT_SECRET"):
            live_scrapers.append(AmadeusLiveScraper())
        
        if not live_scrapers:
            console.print("[bold yellow]⚠️ No live API keys found in environment (SERPAPI_KEY or AMADEUS_CLIENT_ID).[/bold yellow]\n"
                          "[slate-400]To run real live Google Flights queries, sign up for a free API key at https://serpapi.com and run:\n"
                          "  export SERPAPI_KEY='your_api_key'\n"
                          "Falling back to built-in multi-carrier pricing simulation...[/slate-400]\n")
            engine = AeroScrapeEngine()
        else:
            engine = AeroScrapeEngine(scrapers=live_scrapers)
    else:
        engine = AeroScrapeEngine()
    flights, stats = engine.search(query)
    trend = analyze_price_trend(query, current_cheapest=stats.cheapest_price if flights else None, engine=engine)

    display_results(query, flights, stats, trend)


if __name__ == "__main__":
    main()
