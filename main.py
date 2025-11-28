import sys
from src.location_optimization import optimize_coffee_shops
import folium

def main():
    try:
        open_coffeeshops, edges, libraries = optimize_coffee_shops()

        map_osm = folium.Map(location=[41.008, 28.978], zoom_start=11)

        for coffeeshop in open_coffeeshops:
            if coffeeshop in libraries:  
                icon_color = "purple"
                icon_type = "star"
                popup_text = f"{coffeeshop.name} - burada kahve dükkanı açılabilir."
            else:
                icon_color = "red"
                icon_type = "info-circle"  
                popup_text = f"{coffeeshop.name} - burada kahve dükkanı açılabilir."

            folium.Marker(
                [coffeeshop.y, coffeeshop.x],
                icon=folium.Icon(color=icon_color, icon=icon_type),
                popup=folium.Popup(popup_text, parse_html=True)
            ).add_to(map_osm)

        for b in libraries:
            if b not in open_coffeeshops:  
                folium.Marker(
                    [b.y, b.x],
                    icon=folium.Icon(color="blue", icon="book"),  
                    popup=folium.Popup(f"Kütüphane: {b.name}", parse_html=True)
                ).add_to(map_osm)

        for (c, b) in edges:
            coordinates = [[c.y, c.x], [b.y, b.x]]
            map_osm.add_child(folium.PolyLine(coordinates, color="#FF0000", weight=5))

        map_osm.save("coffee_shop_map.html")
        print("Map saved as coffee_shop_map.html")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
