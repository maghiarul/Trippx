from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
import joblib



# Configurarea opțiunilor pentru Chrome (browser vizibil)
options = webdriver.ChromeOptions()
options.add_argument("--lang=en")
options.add_argument("--log-level=3")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Accesăm site-ul Booking.com

def scraper(city_input: str = "Paris"):

    driver.get("https://www.booking.com/")
    city = city_input
    wait = WebDriverWait(driver, 3)

    # Așteptăm caseta de căutare și introducem orașul selectat
    search_box = wait.until(EC.element_to_be_clickable((By.NAME, "ss")))
    driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
    search_box.clear()
    search_box.send_keys(city)
    time.sleep(1)

    # Selectăm datele din calendar
    calendar = wait.until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div/form/div/div[2]/div/div[1]/button[1]")))
    time.sleep(0.5)
    calendar.click()
    data1 = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[3]/div[2]/div/form/div/div[2]/div/div[2]/div/nav/div[2]/div/div[1]/div/div[1]/table/tbody/tr[1]/td[3]/span")))
    time.sleep(0.5)
    data1.click()
    data2 = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[3]/div[2]/div/form/div/div[2]/div/div[2]/div/nav/div[2]/div/div[1]/div/div[1]/table/tbody/tr[1]/td[5]/span")))
    time.sleep(0.5)
    data2.click()

    # Apăsăm butonul de căutare
    button_search = wait.until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div/form/div/div[4]/button")))
    button_search.click()
    time.sleep(5)

    target_count = 10 # Numărul minim de hoteluri pe care dorim să le colectăm
    load_more_css = "button.a83ed08757.c21c56c305.bf0537ecb5.f671049264.af7297d90d.c0e0affd09"
    attempts = 0
    max_attempts = 10

    # Derulăm și încercăm să apăsăm butonul "Load More" dacă este disponibil
    while attempts < max_attempts:
        # Count cards using the updated selector:
        cards = driver.find_elements(By.CSS_SELECTOR, "a[data-testid='title-link']")
        # make cards have 10 elements
        if len(cards) > 10:
            cards = cards[:10]
        count = len(cards)
        print(f"Attempt {attempts}: Found {count} cards.")

        if count >= target_count:
            break

        # Derulăm pagina pentru a încărca mai multe rezultate
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for new content to load

        #Scroll pana la butonul de load more
        driver.execute_script("window.scrollBy(0, -window.innerHeight);")
        time.sleep(2)

        try:
            load_more = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, load_more_css)))
            load_more.click()
        except Exception as e:
            print(f"Load More button not found or not clickable: {e}")
            break

        attempts += 1


    cards = driver.find_elements(By.CSS_SELECTOR, "a[data-testid='title-link']")
    print(f"Final card count: {len(cards)}")

    # Parcurge fiecare hotel din lista cards și extrage link-ul către pagina individuală a hotelului.
    hotel_links = [card.get_attribute("href") for card in cards]

    hotels_data = []
    detailed_ratings = []

    # Iterăm prin fiecare hotel și extragem informațiile relevante
    for idx, link in enumerate(hotel_links):
        print(f"Processing card {idx + 1}/{len(hotel_links)}")
        # Deschide in alt tab
        driver.execute_script("window.open(arguments[0]);", link)
        time.sleep(2)  # Permite sa deschida tab nou


        driver.switch_to.window(driver.window_handles[-1])

        # Extragerea numelui hotelului
        try:
            hotel_name = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[4]/div/div[4]/div[1]/div[1]/div[1]/div[1]/div[2]/div[4]/div[1]/div/div/h2")
                )
            ).text.strip()
        except Exception as e:
            print(f"Could not find hotel name on page: {e}")
            hotel_name = "N/A"

        # Extragerea ratingului general
        try:
            rating = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH,
                    "/html/body/div[4]/div/div[4]/div[1]/div[1]/div[7]/div/div[2]/div/div[3]/div/button/div/div/div[1]/div")
                )
            ).text.strip()
        except Exception as e:
            print(f"Could not find rating on page: {e}")
            rating = "N/A"

            # Extragerea imaginii hotelului
        try:
            hotel_image = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//img[contains(@class, 'e3fa9175ee d354f8f44f ba6d792fd4 b1a5e281e7')]"))
            ).get_attribute("src")
        except Exception as e:
            print(f"Could not find hotel image: {e}")
            hotel_image = "N/A"

        # Extragerea ratingurilor detaliate
        try:
            rating_elements = driver.find_elements(By.XPATH, "//div[contains(@id, '-label')]")
            if len(rating_elements) >= 7:
                staff = rating_elements[7].text.strip()
                facilities = rating_elements[8].text.strip()
                cleanliness = rating_elements[9].text.strip()
                comfort = rating_elements[10].text.strip()
                value = rating_elements[11].text.strip()
                location = rating_elements[12].text.strip()
                wifi = rating_elements[13].text.strip()

                detailed_ratings = [staff, facilities, cleanliness, comfort, value, location, wifi]
            else:
                staff = facilities = cleanliness = comfort = value = location = wifi = "N/A"
        except Exception as e:
            print(f"Could not extract category ratings: {e}")
            staff = facilities = cleanliness = comfort = value = location = wifi = "N/A"

        print("=" * 50)
        field_width = 20
        print(f"{'Name':<{field_width}}: {hotel_name}")
        print(f"{'Rating':<{field_width}}: {rating}")
        print(f"{'Staff':<{field_width}}: {staff}")
        print(f"{'Facilities':<{field_width}}: {facilities}")
        print(f"{'Cleanliness':<{field_width}}: {cleanliness}")
        print(f"{'Comfort':<{field_width}}: {comfort}")
        print(f"{'Value for money':<{field_width}}: {value}")
        print(f"{'Location':<{field_width}}: {location}")
        print(f"{'Wifi':<{field_width}}: {wifi}")
        print(f"{'Image':<{field_width}}: {hotel_image}")
        print("=" * 50)

        # Adăugăm toate datele în listă
        hotels_data.append({
            "Name": hotel_name,
            "Rating": rating,
            "DetailedRatings": detailed_ratings,
            "ImageURL": hotel_image,
        })

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)

    print("Collected hotel data:")
    for hotel in hotels_data:
        print(hotel)

    df = pd.DataFrame(hotels_data)

    df.to_csv("E:/@py_proj/tripper/tripx/src/booking_hotels_cleaned.csv", index=False, encoding="utf-8")
    driver.quit()


    #A doua cerinta


    df = pd.read_csv("E:/@py_proj/tripper/tripx/src/booking_hotels_cleaned.csv", encoding="utf-8")

    # Eliminăm "Scored" din Rating și transformăm în numeric
    df["Rating"] = df["Rating"].str.replace("Scored", "").str.strip()
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")

    print("✅ Textul 'Scored' a fost eliminat din Rating!")

    print(f"📊 După eliminarea rândurilor cu N/A: {df.shape[0]} rânduri rămase")

    # Definim caracteristicile specifice
    features = ["Staff", "Facilities", "Cleanliness", "Comfort", "Value_for_money", "Location", "Wifi"]

    # Înlocuim 'N/A' cu NaN în toate coloanele înainte de conversia `DetailedRatings`
    df.replace("N/A", np.nan, inplace=True)
    #Eliminarea duplicatelor
    df.drop_duplicates(inplace=True)

    # Convertim lista din `DetailedRatings` într-un set de coloane individuale
    import ast
    df[features] = df["DetailedRatings"].apply(lambda x: pd.Series(ast.literal_eval(x)) if isinstance(x, str) and len(ast.literal_eval(x)) == len(features) else pd.Series([np.nan] * len(features)))

    # Eliminăm rândurile unde cel puțin o coloană din `features` conține NaN
    df.dropna(inplace=True)  # Elimină orice rând care conține cel puțin un NaN

    print(f"📊 După eliminarea rândurilor cu N/A: {df.shape[0]} rânduri rămase")


    # Eliminăm coloana originală, care nu mai este necesară
    df.drop(columns=["DetailedRatings"], inplace=True)

    print("✅ Caracteristicile au fost separate în coloane!")
    print(df.head())  # Afișăm primele 5 rânduri pentru verificare

    df.to_csv("E:/@py_proj/tripper/tripx/src/booking_hotels_cleaned.csv", index=False, encoding="utf-8")
    print("✅ Datele curățate au fost salvate în 'booking_hotels_cleaned.csv'.")

    return True

# df = pd.read_csv("D:/Python_project/booking_hotels_cleaned.csv", encoding="utf-8")

# # Selectăm caracteristicile relevante (fără numele hotelului)
# X = df[["Staff", "Facilities", "Cleanliness", "Comfort", "Value_for_money", "Location", "Wifi"]]
# y = df["Rating"]  # Rating-ul ca variabilă țintă

# # Alegem cele mai relevante 5 caracteristici folosind testul ANOVA F-value
# selector = SelectKBest(score_func=f_classif, k=5)
# X_new = selector.fit_transform(X, y)

# # Afișăm caracteristicile selectate
# selected_features = X.columns[selector.get_support()]
# print("📊 Caracteristicile relevante pentru predicție:", selected_features.tolist())


# #A treia cerinta


# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestRegressor
# from xgboost import XGBRegressor
# from sklearn.metrics import mean_squared_error, r2_score

# # Încărcăm datele curățate
# df = pd.read_csv("D:/Python_project/booking_hotels_cleaned.csv", encoding="utf-8")

# # Definim variabilele explicative și variabila țintă
# X = df[["Staff", "Facilities", "Cleanliness", "Comfort", "Value_for_money", "Location", "Wifi"]]
# y = df["Rating"]

# # Împărțim datele în seturi de antrenare și testare (80%-20%)
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # 🌲 **Random Forest**
# rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
# rf_model.fit(X_train, y_train)
# y_pred_rf = rf_model.predict(X_test)

# # ⚡ **XGBoost**
# xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
# xgb_model.fit(X_train, y_train)
# y_pred_xgb = xgb_model.predict(X_test)

# # 🔹 Evaluarea performanței
# mse_rf = mean_squared_error(y_test, y_pred_rf)
# r2_rf = r2_score(y_test, y_pred_rf)

# mse_xgb = mean_squared_error(y_test, y_pred_xgb)
# r2_xgb = r2_score(y_test, y_pred_xgb)

# # 📊 Afișăm rezultatele
# print("\n🌲 **Random Forest**")
# print(f"🔹 Eroare MSE: {mse_rf:.4f}")
# print(f"🔹 R²: {r2_rf:.4f}")

# print("\n ⚡ **XGBoost**")
# print(f"🔹 Eroare MSE: {mse_xgb:.4f}")
# print(f"🔹 R²: {r2_xgb:.4f}")

# joblib.dump(rf_model, "D:/Python_project/random_forest_model.pkl")
# joblib.dump(xgb_model, "D:/Python_project/xgb_model.pkl")

# input("Press ENTER to close the browser...")




