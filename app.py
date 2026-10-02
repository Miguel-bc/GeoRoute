import os
import sys
import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import MarkerCluster

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
        self.setWindowTitle("GeoRoute - Clúster de Portales")
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

        self.consola = QTextEdit()
        self.consola.setReadOnly(True)
        self.consola.setPlaceholderText(
            "Aquí aparecerá el registro de actividad y mensajes..."
        )
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
        self.consola.append("Aplicación iniciada correctamente. Mapa base centrado en España.")

    def inicializar_mapa_espana(self):
        # Coordenadas centrales de España (Madrid / Centro peninsular)
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
            # Cargar capa de portales
            self.gdf_portales = gpd.read_file(archivo, layer="portalpk_publi")
            self.consola.append(f"✔️ Capa de portales cargada: {len(self.gdf_portales):,} registros.")

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

            self.consola.append(f"✔️ Archivo CSV cargado con éxito: {len(self.df_urr):,} registros.")
            self.consola.append(f"📊 Columnas disponibles: {list(self.df_urr.columns)}")

            

        except Exception as e:
            self.consola.append(f"❌ Error al leer el archivo CSV: {str(e)}")


    def generar_mapa_clusters(self):
        try:
            self.consola.append("⚙️ Procesando coordenadas y creando clústeres de portales.")

            df = self.gdf_portales.copy()
            df["cod_postal"] = df["cod_postal"].fillna("00000").astype(str)
            df_wgs84 = df.to_crs(epsg=4326)
            self.consola.append("✅ Datos limpios y transformados a WGS84")

            # Calcular centro específico de los datos cargados para hacer zoom automático al archivo
            minx, miny, maxx, maxy = df_wgs84.total_bounds
            centro_lat = (miny + maxy) / 2
            centro_lon = (minx + maxx) / 2

            # Crear mapa centrado en los datos
            mapa = folium.Map(
                location=[centro_lat, centro_lon],
                zoom_start=12,
                tiles="OpenStreetMap",
            )

            # Crear el contenedor de clústeres optimizado
            marker_cluster = MarkerCluster(name="Portales Clúster").add_to(mapa)

            # Paleta de colores para diferenciar según el código postal
            colores = [
                "red", "blue", "green", "purple", "orange", 
                "darkred", "darkblue", "cadetblue", "darkgreen"
            ]

            # Diccionario dinámico para asignar un color consistente a cada código postal
            cp_colores = {}

            # Iterar sobre los puntos e insertarlos en el clúster
            for _, row in df_wgs84.iterrows():
                geom = row.geometry
                if geom is None or geom.is_empty:
                    continue
                
                lat, lon = geom.y, geom.x
                cp = row["cod_postal"]

                if cp not in cp_colores:
                    cp_colores[cp] = colores[len(cp_colores) % len(colores)]
                
                color_icono = cp_colores[cp]

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color=color_icono,
                    fill=True,
                    fill_color=color_icono,
                    fill_opacity=0.7,
                    tooltip=f"Código Postal: {cp}"
                ).add_to(marker_cluster)

            # Renderizar HTML en el QWebEngineView
            html_content = mapa.get_root().render()
            self.web_view.setHtml(html_content, QUrl("https://localhost"))

            self.consola.append(f"🎉 ¡Clústeres generados con éxito! ({len(df_wgs84):,} portales mapeados)")

        except Exception as e:
            self.consola.append(f"❌ Error al generar los clústeres: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())