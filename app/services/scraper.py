import httpx
import json
from bs4 import BeautifulSoup
from core.config import DEFAULT_HEADERS, REQUEST_TIMEOUT
from schemas.vehicle import Vehicle


class ScraperService:
    @staticmethod
    def fetch_html(url: str) -> str:
        with httpx.Client(
            headers=DEFAULT_HEADERS,
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text

    @staticmethod
    def extract_vehicle_data(html: str, url: str) -> Vehicle:
        soup = BeautifulSoup(html, "lxml")
        vehicle = Vehicle(source_url=url)
        
        title_tag = soup.find("title")
        if title_tag:
            vehicle.title = title_tag.text.strip()
            
        ld_json_scripts = soup.find_all("script", type="application/ld+json")
        for script in ld_json_scripts:
            if not getattr(script, "string", None):
                continue
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get("@type") == "Vehicle":
                        vehicle.make = data.get("brand", {}).get("name")
                        vehicle.model = data.get("model")
                        vehicle.exterior_color = data.get("color")
                        
                        mileage = data.get("mileageFromOdometer", {})
                        if isinstance(mileage, dict):
                            vehicle.mileage = mileage.get("value")
                            
                        engine = data.get("vehicleEngine", {})
                        if isinstance(engine, dict):
                            power = engine.get("enginePower", {})
                            if isinstance(power, dict):
                                power_val = power.get("value")
                                if power_val:
                                    try:
                                        vehicle.power_kw = int(float(power_val))
                                    except ValueError:
                                        pass

                        offers = data.get("offers", {})
                        if isinstance(offers, dict):
                            price = offers.get("price")
                            if price:
                                vehicle.price = float(price)
                            vehicle.currency = offers.get("priceCurrency", "EUR")
                            seller = offers.get("seller", {})
                            if isinstance(seller, dict):
                                vehicle.seller_name = seller.get("name")
            except Exception:
                pass
                
        next_data_script = soup.find("script", id="__NEXT_DATA__")
        if next_data_script and getattr(next_data_script, "string", None):
            try:
                next_data = json.loads(next_data_script.string)
                props = next_data.get("props", {}).get("pageProps", {})
                listing = props.get("listingDetails", {}) or props.get("listing", {}) or {}
                
                vehicle_data = listing.get("vehicle", {})
                
                if vehicle_data:
                    vehicle.make = vehicle.make or vehicle_data.get("make")
                    vehicle.model = vehicle.model or vehicle_data.get("model")
                    vehicle.model_version = vehicle_data.get("modelVersion") or vehicle_data.get("version")
                    vehicle.year = vehicle_data.get("firstRegistrationYear")
                    vehicle.mileage = vehicle.mileage or vehicle_data.get("mileage")
                    vehicle.fuel_type = vehicle_data.get("fuelType")
                    vehicle.transmission = vehicle_data.get("transmission")
                    vehicle.category = vehicle_data.get("category")
                    vehicle.condition = vehicle_data.get("condition")
                    
                    power = vehicle_data.get("power", {}) or {}
                    power_hp = power.get("hp")
                    power_kw = power.get("kw")
                    if power_hp is not None:
                        vehicle.power_hp = vehicle.power_hp or int(power_hp)
                    if power_kw is not None:
                        vehicle.power_kw = vehicle.power_kw or int(power_kw)
                    
                    vehicle.previous_owners = vehicle_data.get("previousOwners")
                
                prices = listing.get("prices", {}) or listing.get("price", {})
                if isinstance(prices, dict):
                    price_val = prices.get("publicPrice") or prices.get("amount") or prices.get("consumerPrice")
                    if price_val:
                        try:
                            vehicle.price = vehicle.price or float(price_val)
                        except (ValueError, TypeError):
                            pass
                    
                seller = listing.get("seller", {})
                if isinstance(seller, dict):
                    vehicle.seller_type = seller.get("type")
                    vehicle.seller_name = vehicle.seller_name or seller.get("companyName") or seller.get("name")
                    vehicle.seller_city = seller.get("city")
                    vehicle.seller_country = seller.get("countryCode")
                    vehicle.zip_code = seller.get("zipCode")

                images = listing.get("images", [])
                if isinstance(images, list):
                    # extract imageUrls or plain strings
                    img_list = []
                    for img in images:
                        if isinstance(img, str):
                            img_list.append(img)
                        elif isinstance(img, dict) and img.get("url"):
                            img_list.append(img.get("url"))
                    vehicle.images = img_list
            except Exception:
                pass
                
        return vehicle

    @classmethod
    def scrape(cls, url: str) -> Vehicle:
        html = cls.fetch_html(url)
        return cls.extract_vehicle_data(html, url)
