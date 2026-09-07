"""Create a print-ready PDF report from the verified experiment artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = PROJECT_ROOT / "artifacts"
REPORT_PATH = PROJECT_ROOT / "reports" / "Stock_Price_Prediction_Report.pdf"
NAVY = colors.HexColor("#1F4E78")
PALE_BLUE = colors.HexColor("#EAF2F8")
LIGHT_GRAY = colors.HexColor("#D9D9D9")


def metric_table(rows: list[list[str]], widths: list[float]) -> Table:
    table = Table(rows, colWidths=[width * inch for width in widths], repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_BLUE]),
            ]
        )
    )
    return table


def footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LIGHT_GRAY)
    canvas.line(document.leftMargin, 0.48 * inch, A4[0] - document.rightMargin, 0.48 * inch)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(document.leftMargin, 0.31 * inch, "Stock Price Prediction Minor Project")
    canvas.drawRightString(A4[0] - document.rightMargin, 0.31 * inch, f"Page {document.page}")
    canvas.restoreState()


def main() -> None:
    metrics = json.loads((ARTIFACTS / "metrics.json").read_text(encoding="utf-8"))
    summary = json.loads((ARTIFACTS / "dataset_summary.json").read_text(encoding="utf-8"))
    chart = ARTIFACTS / "forecast.png"
    if not chart.is_file():
        raise FileNotFoundError(f"Missing chart: {chart}")

    ridge = metrics["metrics"]["ridge_regression"]
    baseline = metrics["metrics"]["naive_persistence"]
    source = summary["source"]
    date_range = summary["date_range"]

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(REPORT_PATH),
        pagesize=A4,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="Stock Price Prediction Minor Project Report",
        author="Siddhant",
    )
    styles = getSampleStyleSheet()
    cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=15,
    )
    cover_subtitle = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=14,
        leading=19,
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.black,
        spaceBefore=13,
        spaceAfter=7,
        keepWithNext=True,
    )
    subheading = ParagraphStyle(
        "Subheading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.black,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.2,
        leading=14.2,
        textColor=colors.black,
        alignment=TA_LEFT,
        spaceAfter=7,
    )
    bullet = ParagraphStyle(
        "Bullet",
        parent=body,
        leftIndent=14,
        firstLineIndent=-8,
        bulletIndent=5,
        spaceAfter=4,
    )
    caption = ParagraphStyle(
        "Caption",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=8.8,
        leading=11,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=9,
    )

    story = [Spacer(1, 1.7 * inch)]
    story.append(Paragraph("Stock Price Prediction Minor Project Report", cover_title))
    story.append(Paragraph("Chronological Evaluation with Ridge Regression", cover_subtitle))
    story.append(Spacer(1, 0.3 * inch))
    for line in (
        "Prepared by Siddhant",
        "Minor Project",
        f"Dataset {source} daily closing prices",
        f"Verified period {date_range['first_observation']} to {date_range['last_observation']}",
        "Repository https://github.com/Siddhantkr07/ML-Minor",
    ):
        story.append(Paragraph(line, cover_subtitle))
    story.append(PageBreak())

    story.append(Paragraph("Abstract", heading))
    story.append(
        Paragraph(
            "This project evaluates whether a regression model can forecast the next trading day's closing price from recent price history. "
            f"Daily {source} data from {date_range['first_observation']} to {date_range['last_observation']} was retrieved through Yahoo Finance using yfinance. "
            "The model creates lag, return, and rolling-window features and is evaluated on the newest 20 percent of eligible observations. "
            f"Ridge Regression achieved MAE {ridge['mae']:.4f}, RMSE {ridge['rmse']:.4f}, and R-squared {ridge['r2']:.4f}. "
            f"The naive persistence baseline achieved a lower MAE of {baseline['mae']:.4f}, so it remained the stronger benchmark for this run. "
            "The project is an educational forecasting experiment and not investment advice.",
            body,
        )
    )

    story.append(Paragraph("Problem Statement", heading))
    story.append(
        Paragraph(
            "The objective is to estimate the next trading day's closing price using only information available at the end of the current trading day. "
            "This is a time-series regression problem, so the model must be evaluated on a later period rather than on randomly shuffled rows.",
            body,
        )
    )

    story.append(Paragraph("Project Objectives", heading))
    for item in (
        "Retrieve and validate historical daily closing-price data.",
        "Construct predictive features without using future prices as inputs.",
        "Train a reproducible Ridge Regression pipeline.",
        "Compare the model against a chronological holdout set and naive benchmark.",
        "Save the chart, metrics, predictions, dataset snapshot, and trained model for each run.",
    ):
        story.append(Paragraph(item, bullet, bulletText="-"))

    story.append(Paragraph("Dataset", heading))
    story.append(
        Paragraph(
            "The verified experiment uses Apple Inc. stock history with ticker AAPL. The data loader accepts Yahoo Finance downloads or a local CSV with Date and Close columns. "
            "It sorts dates, retains the final occurrence of any duplicate date, converts close values to numeric form, removes invalid values, and requires positive closing prices.",
            body,
        )
    )
    story.append(
        metric_table(
            [
                ["Attribute", "Verified value"],
                ["Data source", "Yahoo Finance through yfinance"],
                ["Ticker", source],
                ["Observed date range", f"{date_range['first_observation']} to {date_range['last_observation']}"],
                ["Trading-day observations", str(summary["observations"])],
                ["Close price range", f"{summary['close_price']['minimum']:.2f} to {summary['close_price']['maximum']:.2f}"],
                ["Mean close price", f"{summary['close_price']['mean']:.2f}"],
            ],
            [2.5, 3.55],
        )
    )

    story.append(Paragraph("Feature Engineering", heading))
    story.append(
        Paragraph(
            "For a row dated t, the target is the closing price at t plus one trading day. Every input feature is calculated from the current or earlier closing prices. "
            "This construction prevents the model from reading the future target while training or evaluating.",
            body,
        )
    )
    story.append(
        metric_table(
            [
                ["Feature group", "Variables used"],
                ["Current price", "Current closing price"],
                ["Lagged price", "1, 2, 3, 5, 10, and 20 trading-day lags"],
                ["Momentum", "Daily percentage return"],
                ["Rolling statistics", "5, 10, and 20-day means and standard deviations"],
                ["Relative price", "Distance from each rolling mean"],
            ],
            [1.75, 4.3],
        )
    )

    story.append(Paragraph("Model and Evaluation Design", heading))
    story.append(
        Paragraph(
            "The model pipeline applies median imputation, standard scaling, and Ridge Regression with alpha equal to 1.0. "
            "The latest 20 percent of completed rows is reserved as a chronological test set. The baseline predicts that the next close equals the current close.",
            body,
        )
    )
    story.append(
        metric_table(
            [
                ["Experiment setting", "Verified value"],
                ["Forecast horizon", f"{metrics['forecast_horizon_trading_days']} trading day"],
                ["Training rows", str(metrics["train_rows"])],
                ["Test rows", str(metrics["test_rows"])],
                ["Primary model", "Median imputation + StandardScaler + Ridge Regression"],
                ["Comparison model", "Naive persistence baseline"],
            ],
            [2.25, 3.8],
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("Results", heading))
    story.append(
        Paragraph(
            "Results below come from the final chronological holdout period. Lower MAE and RMSE are better; higher R-squared is better.",
            body,
        )
    )
    story.append(
        metric_table(
            [
                ["Model", "MAE", "RMSE", "R-squared"],
                ["Ridge Regression", f"{ridge['mae']:.4f}", f"{ridge['rmse']:.4f}", f"{ridge['r2']:.4f}"],
                ["Naive persistence", f"{baseline['mae']:.4f}", f"{baseline['rmse']:.4f}", f"{baseline['r2']:.4f}"],
            ],
            [2.35, 1.15, 1.25, 1.3],
        )
    )
    chart_image = Image(str(chart), width=6.0 * inch, height=3.38 * inch)
    story.append(KeepTogether([Spacer(1, 10), chart_image, Paragraph("Figure 1. Chronological holdout predictions for AAPL.", caption)]))

    story.append(Paragraph("Discussion", heading))
    story.append(
        Paragraph(
            "Ridge Regression follows the broad movement of the actual closing-price series and produces a high R-squared on this holdout period. "
            "However, the naive persistence baseline achieves lower MAE and RMSE and slightly higher R-squared. Therefore, the Ridge model did not improve on the simple current-close prediction for this particular experiment. "
            "This comparison is important because it prevents overstatement of the forecast's practical performance.",
            body,
        )
    )

    story.append(Paragraph("Limitations", heading))
    for item in (
        "Only historical closing prices are used; news, earnings, fundamentals, macroeconomic data, and intraday signals are excluded.",
        "The experiment covers one asset and one holdout period, so results may not generalize to other stocks or market regimes.",
        "Trading costs, portfolio risk, and investment suitability are not assessed.",
        "The output is not financial advice and must not be used as an automated trading signal.",
    ):
        story.append(Paragraph(item, bullet, bulletText="-"))

    story.append(Paragraph("Reproducibility", heading))
    story.append(
        Paragraph(
            "The repository includes source code, automated tests, the dataset documentation, and the model card. Run the following commands from the project root after installing dependencies:",
            body,
        )
    )
    story.append(
        Paragraph(
            "$env:PYTHONPATH = \"src\"<br/>.\\.venv\\Scripts\\python.exe -m stock_predictor.cli train --ticker AAPL --start 2020-01-01 --end 2025-01-01",
            ParagraphStyle("Command", parent=body, fontName="Courier", fontSize=8.6, leading=12, leftIndent=12, spaceBefore=3, spaceAfter=8),
        )
    )

    story.append(Paragraph("Conclusion", heading))
    story.append(
        Paragraph(
            "This project provides a reproducible next-day stock-price forecasting workflow with data validation, leakage-aware features, chronological evaluation, automated tests, and documented outputs. "
            "The verified AAPL experiment shows that Ridge Regression can track price movements, while the naive baseline remains stronger on the selected holdout metrics. "
            "Future work should evaluate walk-forward validation, multiple assets, and carefully validated additional predictors.",
            body,
        )
    )

    story.append(Paragraph("References", heading))
    for item in (
        "Yahoo Finance data accessed through yfinance. https://github.com/ranaroussi/yfinance",
        "scikit-learn Ridge Regression documentation. https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html",
        "Hyndman, R. J., and Athanasopoulos, G. Forecasting Principles and Practice. https://otexts.com/fpp3/tscv.html",
        "Project repository. https://github.com/Siddhantkr07/ML-Minor",
    ):
        story.append(Paragraph(item, bullet, bulletText="-"))

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Created {REPORT_PATH}")


if __name__ == "__main__":
    main()
