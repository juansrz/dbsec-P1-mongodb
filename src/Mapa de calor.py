import pandas as pd
from folium import Map
from folium.plugins import HeatMap

if __name__ == '__main__':
    df = pd.read_csv('resultados2.csv')
    for_map = Map()
    hm_wide = HeatMap(
        list(zip(df.get("end station latitude").values, df.get("end station longitude").values)),
        min_opacity=0.2,
        radius=17,
        blur=15,
        max_zoom=1,
    )
    for_map.add_child(hm_wide)
    for_map.save("Heatmap.html")
    for_map.show_in_browser()
