import os
import sys
import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView


class VentanaPrincipal(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoRoute")
        self.setGeometry(100, 100, 1200, 750)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFCC00;
            }
        """)

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(15, 15, 15, 15)
        layout_principal.setSpacing(15)

        # Panel Izquierdo
        panel_izquierdo = QWidget()
        layout_izquierdo = QVBoxLayout(panel_izquierdo)
        layout_izquierdo.setContentsMargins(0, 0, 0, 0)

        self.btn_cargar = QPushButton("📁 Cargar Archivo GPKG")
        self.btn_cargar.setStyleSheet("""
            QPushButton {
                background-color: #D40511;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #B3040E;
            }
        """)
        self.btn_cargar.clicked.connect(self.cargar_archivo_gpkg)
        layout_izquierdo.addWidget(self.btn_cargar)

        self.btn_urr = QPushButton("🌐 URR")
        self.btn_urr.setStyleSheet("""
            QPushButton {
                background-color: #D40511;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #B3040E;
            }
        """)
        self.btn_urr.clicked.connect(self.cargar_archivo_urr)
        layout_izquierdo.addWidget(self.btn_urr)

        self.btn_generar = QPushButton("🌐 Generar Mapa")
        self.btn_generar.setStyleSheet("""
            QPushButton {
                background-color: #D40511;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #B3040E;
            }
        """)
        self.btn_generar.clicked.connect(self.generar_mapa_inicial)
        layout_izquierdo.addWidget(self.btn_generar)

        self.consola = QTextEdit()
        self.consola.setReadOnly(True)        
        self.consola.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #222222;
                border: 2px solid #D40511;
                border-radius: 6px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                padding: 8px;
            }
        """)
        layout_izquierdo.addWidget(self.consola)

        layout_principal.addWidget(panel_izquierdo, stretch=1)

        # Panel Derecho (Visor Web para el Mapa)
        self.panel_derecho = QWidget()
        self.panel_derecho.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 2px solid #CCCCCC;
                border-radius: 8px;
            }
        """)
        layout_derecho = QVBoxLayout(self.panel_derecho)
        layout_derecho.setContentsMargins(5, 5, 5, 5)

        # Componente web para renderizar Folium
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )
        layout_derecho.addWidget(self.web_view)

        layout_principal.addWidget(self.panel_derecho, stretch=2)

        # Cargar el mapa base centrado en España al iniciar
        self.inicializar_mapa_espana()
        self.consola.append("✔️ Aplicación iniciada correctamente. Mapa base centrado en España.")

    def inicializar_mapa_espana(self):
        lat_espana = 40.4168
        lon_espana = -3.7038

        mapa_base = folium.Map(
            location=[lat_espana, lon_espana],
            zoom_start=6,  
            tiles="OpenStreetMap",
        )

        html_content = mapa_base.get_root().render()
        self.web_view.setHtml(html_content, QUrl("https://localhost"))

    def cargar_archivo_gpkg(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Archivo Geopackage",
            "",
            "Archivos GPKG (*.gpkg)",
        )

        if not archivo:
            return

        self.archivo_cargado = archivo
        nombre_corto = os.path.basename(archivo)
        self.consola.append(f"\n📂 Archivo seleccionado: {nombre_corto}")

        try:
            self.gdf_portales = gpd.read_file(archivo, layer="portalpk_publi")
            self.consola.append(f"✅ Capa de portales cargada: {len(self.gdf_portales):,} registros.")

        except Exception as e:
            self.consola.append(f"❌ Error al leer la capa de portales del GPKG: {str(e)}")

    def cargar_archivo_urr(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Archivo CSV",
            "",
            "Archivos CSV (*.csv)",
        )

        if not archivo:
            return

        self.archivo_cargado = archivo
        nombre_corto = os.path.basename(archivo)
        self.consola.append(f"\n📂 Archivo seleccionado: {nombre_corto}")

        try:            
            try:
                self.df_urr = pd.read_csv(archivo, sep=";", encoding='utf-8')
            except UnicodeDecodeError:
                self.df_urr = pd.read_csv(archivo, sep=";", encoding='latin1')

            self.consola.append(f"✅ Archivo CSV cargado con éxito: {len(self.df_urr):,} registros.")
            self.consola.append(f"📊 Columnas disponibles: {list(self.df_urr.columns)}")            

        except Exception as e:
            self.consola.append(f"❌ Error al leer el archivo CSV: {str(e)}")

    def generar_mapa_inicial(self):
        self.generar_mapa_clusters()
        
    def generar_mapa_clusters(self):
        try:
            self.consola.append("⚙️ Procesando coordenadas y creando clústeres por vehículo...")

            df = self.gdf_portales.copy()
            df["cod_postal"] = df["cod_postal"].fillna("00000").astype(str)  
            
            df_urr_temp = self.df_urr.copy()
            df_urr_temp["Codigo Postal"] = df_urr_temp["Codigo Postal"].fillna(0).astype(str)
            df_urr_temp = df_urr_temp.drop_duplicates(subset=["Codigo Postal"], keep="first")
            
            df = df.merge(
                df_urr_temp[["Codigo Postal", "Codigo Vehiculo"]], 
                left_on="cod_postal", 
                right_on="Codigo Postal",  
                how="left"
            )
            df["Codigo Vehiculo"] = df["Codigo Vehiculo"].fillna("Sin Vehículo Asignado")
            self.consola.append(f"✅ Vehículos integrados correctamente ({len(df):,} portales únicos).")
            
            df_wgs84 = df.to_crs(epsg=4326)
            self.consola.append("✅ Datos limpios y transformados a WGS84")
            
            minx, miny, maxx, maxy = df_wgs84.total_bounds
            centro_lat = (miny + maxy) / 2
            centro_lon = (minx + maxx) / 2
            
            # Inicializamos el mapa con el centro calculado de Murcia y aplicamos fit_bounds
            mapa = folium.Map(
                location=[centro_lat, centro_lon],
                zoom_start=11,
                tiles="OpenStreetMap",
            )
            mapa.fit_bounds([[miny, minx], [maxy, maxx]])

            self.consola.append("🎨 Agrupando puntos y asignando colores por vehículo...")

            colores_disponibles = [
                "red", "blue", "green", "purple", "orange", 
                "darkred", "darkblue", "cadetblue", "darkgreen", "pink"
            ]

            vehiculos_unicos = df_wgs84["Codigo Vehiculo"].unique()
            
            vehiculo_colores = {
                veh: colores_disponibles[i % len(colores_disponibles)] 
                for i, veh in enumerate(vehiculos_unicos)
            }

            for vehiculo in vehiculos_unicos:
                df_veh = df_wgs84[df_wgs84["Codigo Vehiculo"] == vehiculo]
                color_actual = vehiculo_colores[vehiculo]

                layer_group = folium.FeatureGroup(name=f"Vehículo: {vehiculo}").add_to(mapa)

                data_puntos = []
                for geom, cp in zip(df_veh.geometry, df_veh["cod_postal"]):
                    if geom is not None and not geom.is_empty:
                        data_puntos.append([
                            geom.y, 
                            geom.x, 
                            f"CP: {cp} | Vehículo: {vehiculo}"
                        ])

                if data_puntos:
                    FastMarkerCluster(
                        data=data_puntos,
                        name=f"Clúster {vehiculo}",
                        overlay=True,
                        control=True,
                        icon_create_function=f"""
                            function(cluster) {{
                                return L.divHtmlIcon({{
                                    html: '<div style="background-color: {color_actual}; color: white; border-radius: 50%; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white;">' + cluster.getChildCount() + '</div>',
                                    className: 'custom-cluster-icon',
                                    iconSize: [35, 35]
                                }});
                            }}
                        """
                    ).add_to(layer_group)

            folium.LayerControl(collapsed=False).add_to(mapa)

            html_content = mapa.get_root().render()
            self.web_view.setHtml(html_content, QUrl("https://localhost"))

            self.consola.append(f"🎉 ¡Mapa ajustado y generado con éxito en Murcia ({len(df_wgs84):,} portales)!")

        except Exception as e:
            self.consola.append(f"❌ Error al generar los clústeres: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())