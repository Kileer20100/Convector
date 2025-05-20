import os
import shutil
import asyncio
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import pathname2url

from pdf2image import convert_from_path
from playwright.async_api import async_playwright
from rich.console import Console
from rich.progress import (
    Progress, BarColumn, TextColumn,
    TimeElapsedColumn, SpinnerColumn, TimeRemainingColumn
)
from rich.panel import Panel
from time import sleep
from random import randint, choice

console = Console()

HTML_DIR = "html"
OUTPUT_DIR = "output"
VIEWPORT_WIDTH = 1920
DPI = 600
MAX_CONCURRENT_TASKS = 4

HACK_WORDS = [
    "Initializing Quantum Node", "Bypassing Mainframe", "Decrypting Firewall",
    "Launching Counter-ICE", "Routing via Tor Nodes", "Engaging Stealth Protocol",
    "Sniffing HTML metadata", "Injecting Payload", "Tracking Host IP",
    "Spoofing DNS Tables", "Overriding Permissions", "Establishing Socket Tunnel"
]


def file_path_to_url(path: str) -> str:
    return urljoin('file:', pathname2url(os.path.abspath(path)))


def fake_hack_sequence():
    for _ in range(10):
        msg = choice(HACK_WORDS)
        dots = "." * randint(3, 8)
        console.print(f"[bold green]{msg}{dots}[/bold green]")
        sleep(0.1)


async def convert_html_to_pdf(html_path: Path, pdf_path: Path, progress, task):
    url = file_path_to_url(str(html_path))
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": VIEWPORT_WIDTH, "height": 1080})
        await page.goto(url, wait_until="networkidle")
        total_height = await page.evaluate("document.body.scrollHeight")
        await page.pdf(
            path=str(pdf_path),
            width=f"{VIEWPORT_WIDTH}px",
            height=f"{total_height}px",
            print_background=True,
            prefer_css_page_size=True
        )
        await browser.close()
        progress.update(task, advance=33, description="[yellow]🛰️ PDF uplink complete")


def convert_pdf_to_png(pdf_path: Path, output_folder: Path, progress, task):
    pages = convert_from_path(str(pdf_path), dpi=DPI)
    for i, page in enumerate(pages):
        output_path = output_folder / f"page_{i+1:03d}.png"
        page.save(output_path, "PNG")
        sleep(0.03)
    progress.update(task, advance=33, description="[cyan]📡 PNG frames received")


async def process_html_file(html_file: Path, progress: Progress, semaphore: asyncio.Semaphore):
    async with semaphore:
        name = html_file.stem
        output_subfolder = Path(OUTPUT_DIR) / name
        output_subfolder.mkdir(parents=True, exist_ok=True)

        pdf_path = output_subfolder / "report.pdf"

        console.rule(f"[bold magenta]🛸 INITIATING SEQUENCE: {name} [/bold magenta]")
        fake_hack_sequence()

        task = progress.add_task(f"[green]🚀 Launching vector: {name}", total=100)

        try:
            await convert_html_to_pdf(html_file, pdf_path, progress, task)
            convert_pdf_to_png(pdf_path, output_subfolder, progress, task)
            shutil.copy(html_file, output_subfolder / html_file.name)
            progress.update(task, advance=34, description="[blue]💾 Data extracted")
            sleep(0.2)
            progress.update(task, completed=100, description=f"[bold green]✅ COMPLETE")
            console.print(Panel(f"[bold green]🎯 Target '{name}' neutralized. Data archived.[/bold green]", style="green"))
        except Exception as e:
            progress.update(task, description=f"[red]❌ ERROR: {e}")
            console.print(Panel(f"[bold red]🔥 CRITICAL FAILURE: {e}[/bold red]", style="red"))


async def main():
    html_files = list(Path(HTML_DIR).glob("*.html"))
    if not html_files:
        console.print("[red]❌ No HTML targets found in 'html/' folder.[/red]")
        return

    console.print(Panel("[bold cyan]🛰️ CONNECTING TO GLOBAL GRID...[/bold cyan]", style="cyan"))
    sleep(1.2)
    console.print(Panel(f"[bold magenta]🔍 {len(html_files)} targets identified. Locking coordinates...[/bold magenta]", style="magenta"))
    sleep(0.7)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    with Progress(
        SpinnerColumn(style="bold red"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=50, complete_style="bold green"),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        await asyncio.gather(*[
            process_html_file(html_file, progress, semaphore)
            for html_file in html_files
        ])


if __name__ == "__main__":
    asyncio.run(main())
