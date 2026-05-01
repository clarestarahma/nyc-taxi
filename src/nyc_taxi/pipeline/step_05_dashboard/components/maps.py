import pydeck as pdk
import streamlit as st
import copy
import numpy as np

def get_color_gradient(val, max_val):
  ratio = val / max_val if max_val > 0 else 0
  if ratio < 0.25:
      return [173, 216, 230, 160] # Light Blue
  elif ratio < 0.5:
      return [255, 255, 191, 160] # Yellow
  elif ratio < 0.75:
      return [253, 174, 97, 180]  # Orange
  else:
      return [215, 25, 28, 200]   # Red

def build_map_geojson(geojson_raw, df, metric):
  geojson = copy.deepcopy(geojson_raw)

  if metric == "total_revenue":
    multiplier = 50
  elif metric == "trip_count":
    multiplier = 150 
  else:
    multiplier = 300

  df_map = df.copy()
  df_map["pickup_location_id"] = df_map["pickup_location_id"].astype(str)
  value_map = df_map.set_index("pickup_location_id")[metric].to_dict()
  max_val = max(value_map.values()) if value_map else 0

  for feature in geojson["features"]:
    loc_id = feature["properties"].get("location_id")
    val = value_map.get(loc_id, 0)
    feature["properties"]["metric_value"] = val
    feature["properties"]["fill_color"] = get_color_gradient(val, max_val)
    feature["properties"]["metric_display"] = f"{val:.2f}"
    feature["properties"]["elevation"] = np.log1p(val) * multiplier

  geojson["features"] = [
    f for f in geojson["features"] 
    if f["properties"]["metric_value"] > 0
  ]
  return geojson

def render_nyc_map(geojson_data, df, metric):
  """ Main Component """
  map_ready = build_map_geojson(geojson_data, df, metric)

  tooltip={
    "html": """
        <b>Zona:</b> {zone} <br/>
        <b>Borough:</b> {borough} <br/>
        <b>Value:</b> {metric_display}
    """,
    "style": {"color": "white", "backgroundColor": "#1D4ED8"}
  }

  layer = pdk.Layer(
    "GeoJsonLayer",
    data=map_ready,
    pickable=True,
    filled=True,
    extruded=True,
    get_elevation="properties.elevation", 
    elevation_scale=1,
    get_fill_color="properties.fill_color",
    get_line_color=[255, 255, 255, 50],
  )

  view_state = pdk.ViewState(
    latitude=40.690,   
    longitude=-73.940, 
    zoom=10.0,
    min_zoom=9,
    max_zoom=15,
    pitch=45,
    bearing=0
)

  st.pydeck_chart(pdk.Deck(
      layers=[layer],
      initial_view_state=view_state,
      map_style="light",
      tooltip=tooltip
  ))