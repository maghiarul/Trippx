import csv
import flet as ft
from cards import random_card  # Import the modular card function
from predict_nou import predict_rating
from scraper import scraper
import os
import time

def load_hotel_data(csv_filename: str) -> list:
    """Load hotel data from CSV into a list of dictionaries. Waits until the file exists."""
    while not os.path.exists(csv_filename):
        print(f"Waiting for {csv_filename} to be created...")
        time.sleep(1)  # Wait 1 second before checking again

    hotels = []
    with open(csv_filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hotels.append(row)
    return hotels

def main(page: ft.Page):
    page.title = "RandomTrip"
    page.bgcolor = "#B3DAFF"
    page.window.center = True
    page.window.width = 800
    page.window.height = 1080
    page.window.icon = "assets/icons/logo.png"

    # -------------------------------
    # Initially try to load CSV data (if exists)
    # -------------------------------
    csv_file = "E:/@py_proj/tripper/tripx/src/booking_hotels_cleaned.csv"
    hotels = load_hotel_data(csv_file) if os.path.exists(csv_file) else [] 
    current_index = 0  # Track the current card index

    # Global user prediction values (set via ratings dialog)
    user_pred_rf = None
    user_pred_xgb = None

    # List to store hotels where condition is met
    selected_hotels = []

    # Container to hold the current card widget.
    card_container = ft.Container(alignment=ft.alignment.center)

    # -------------------------------
    # Predictions display widget (placed below the header)
    # -------------------------------
    # Initially show N/A (since no ratings are set)
    pred_text = ft.Text("RF: N/A | XGB: N/A", color="#1F1F1F", size=16, key="pred_text")

    # -------------------------------
    # Ratings Popup Dialog Setup (Modal)
    # -------------------------------
    ratings_fields = ["Staff", "Facilities", "Cleanliness", "Comfort", "Value_for_money", "Location", "Wifi"]
    # Create TextField inputs for each rating.
    ratings_inputs = {
        field: ft.TextField(label=field, value="5.0", width=120, text_align="center")
        for field in ratings_fields
    }

    def close_ratings(e):
        nonlocal user_pred_rf, user_pred_xgb
        # Extract entered values from TextFields into a dict
        rating_data = {field: ratings_inputs[field].value for field in ratings_fields}
        print("User-entered Ratings:", rating_data)
        # Run prediction using the user-entered data
        pred_rf, pred_xgb = predict_rating(rating_data)
        user_pred_rf = round(pred_rf, 2)
        user_pred_xgb = round(pred_xgb, 2)
        # Update the predictions display text widget.
        pred_text.value = f"RF: {user_pred_rf:.2f} | XGB: {user_pred_xgb:.2f}"
        page.close(ratings_dialog)
        page.update()

    ratings_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Set Ratings"),
        content=ft.Column(
            controls=[ratings_inputs[field] for field in ratings_fields],
            spacing=10,
        ),
        actions=[
            ft.TextButton("Confirm", on_click=close_ratings),
            ft.TextButton("Cancel", on_click=lambda e: page.close(ratings_dialog)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Dialog dismissed!"),
    )

    def open_ratings(e):
        page.open(ratings_dialog)
        page.update()

    ratings_button = ft.TextButton(
        content=ft.Row(
            controls=[
                ft.Image(src="icons/settings.svg", width=20, height=20, tooltip="Set Ratings", color="#1f1f1f"),
                ft.Text("Set Ratings", color="#1f1f1f")
            ],
            spacing=5,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        on_click=open_ratings,
        style=ft.ButtonStyle(color="#1f1f1f", bgcolor="white")
    )

    # -------------------------------
    # Header UI (Search Bar + Ratings Button)
    # -------------------------------
    def on_search_submit(e: ft.ControlEvent):
        nonlocal hotels, current_index
        # Access the search query
        search_query = e.control.value
        print("User entered:", search_query)
        # Call scraper with the search query to create the CSV file
        scraper(search_query)
        # Load the hotel data (this will wait until the CSV is created)
        hotels = load_hotel_data(csv_file)
        current_index = 0
        # If hotels were successfully loaded, update the card container.
        if hotels:
            card_tuple = random_card(page, hotels[current_index], on_card_swipe)
            if isinstance(card_tuple, tuple) and len(card_tuple) == 3:
                first_card, _, _ = card_tuple
            else:
                first_card = card_tuple
            card_container.content = first_card
        else:
            card_container.content = ft.Text("No hotel data found after scraping!")
        page.update()

    search = ft.SearchBar(
        width=350,
        bar_hint_text="Where you want to go...",
        bar_leading=ft.Image(src="icons/search.svg", width=16, height=16, tooltip="Search", color="#1F1F1F"),
        bar_padding=ft.padding.only(left=20),
        bar_bgcolor="white",
        bar_hint_text_style=ft.TextStyle(color="#1F1F1F"),
        bar_text_style=ft.TextStyle(color="#1F1F1F"),
        on_submit=on_search_submit  # Callback triggered when user hits Enter.
    )

    header = ft.Row(
        controls=[
            ft.Container(content=search, alignment=ft.alignment.center),
            ft.Container(content=ratings_button, alignment=ft.alignment.center),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # -------------------------------
    # Define swipe callback for the card.
    # -------------------------------
    # We assume random_card now calls this callback with:
    # on_card_swipe(hotel_data, direction, current_pred_rf, current_pred_xgb)
    def on_card_swipe(hotel_data: dict, direction: str, current_pred_rf, current_pred_xgb):
        nonlocal current_index, selected_hotels
        print(f"Swiped {direction} on card: {hotel_data['Name']}")
        # If the user predictions have been set then compare them:
        if user_pred_rf is not None and user_pred_xgb is not None:
            if (user_pred_rf > current_pred_rf) and (user_pred_xgb > current_pred_xgb):
                # Store the hotel info with its predictions
                selected_hotels.append({
                    "Name": hotel_data["Name"],
                    "RF": current_pred_rf,
                    "XGB": current_pred_xgb
                })
        current_index += 1
        if current_index < len(hotels):
            card_tuple = random_card(page, hotels[current_index], on_card_swipe)
            if isinstance(card_tuple, tuple) and len(card_tuple) == 3:
                next_card, _, _ = card_tuple
            else:
                next_card = card_tuple
            card_container.content = next_card
        else:
            card_container.content = ft.Text("No more hotels!")
            show_top_hotels(selected_hotels)
        page.update()

    # -------------------------------
    # Function to display top 5 hotels in a dialog.
    # -------------------------------
    def show_top_hotels(hotels_list):
        if not hotels_list:
            dialog_content = ft.Text("No hotels met your criteria.")
        else:
            hotels_list.sort(key=lambda h: (h["RF"] + h["XGB"]) / 2, reverse=True)
            top5 = hotels_list[:5]
            items = []
            for h in top5:
                items.append(ft.Text(f'{h["Name"]} - RF: {h["RF"]:.2f}, XGB: {h["XGB"]:.2f}'))
            dialog_content = ft.Column(controls=items, spacing=10)
        top_hotels_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Top 5 Hotels"),
            content=dialog_content,
            actions=[ft.TextButton("Close", on_click=lambda e: page.close(top_hotels_dialog))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(top_hotels_dialog)
        page.update()

    # -------------------------------
    # Load the first card (if available)
    # -------------------------------
    if hotels:
        card_tuple = random_card(page, hotels[current_index], on_card_swipe)
        if isinstance(card_tuple, tuple) and len(card_tuple) == 3:
            first_card, _, _ = card_tuple
        else:
            first_card = card_tuple
        card_container.content = first_card
    else:
        card_container.content = ft.Text("No hotel data found.")

    # -------------------------------
    # Main Column (Header + Prediction Display + Card Container)
    # -------------------------------
    main_column = ft.Column(
        controls=[
            header,       # Header row
            pred_text,    # Predictions display placed below header
            card_container,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.add(main_column)
    
ft.app(target=main, assets_dir="assets")
