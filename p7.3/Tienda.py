import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestDemoblazeIntegral(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Configuración inicial."""
        print("Iniciando pruebas en Demoblaze...")
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        # chrome_options.add_argument('--headless') # Descomentar para que no se abra la ventana
        
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.wait = WebDriverWait(cls.driver, 10) # Tiempo máximo de espera: 10 segundos
        cls.base_url = "https://www.demoblaze.com/"

    def test_01_navegacion_y_seleccion(self):
        """CP-01: Filtrar por categoría (Laptops) y seleccionar un producto"""
        self.driver.get(self.base_url)
        
        # 1. Clic en la categoría 'Laptops'
        btn_laptops = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Laptops")))
        btn_laptops.click()
        
        # 2. Esperar a que carguen los productos de la categoría y hacer clic en 'Sony vaio i5'
        producto = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sony vaio i5")))
        producto.click()
        
        # Validación: Verificar que entramos a la página del producto (el título h2 debe ser Sony vaio i5)
        titulo_producto = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "name")))
        self.assertEqual(titulo_producto.text, "Sony vaio i5", "No se cargó la página del producto correcto.")

    def test_02_agregar_al_carrito_y_alerta(self):
        """CP-02: Agregar al carrito y manejar la alerta de Javascript"""
        # 1. Clic en el botón "Add to cart"
        btn_add_cart = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add to cart")))
        btn_add_cart.click()
        
        # 2. Demoblaze lanza una alerta nativa del navegador. Debemos esperarla y aceptarla.
        self.wait.until(EC.alert_is_present())
        alerta = self.driver.switch_to.alert
        self.assertEqual(alerta.text, "Product added", "El texto de la alerta no es el esperado.")
        alerta.accept() # Esto simula hacer clic en "Aceptar" en la alerta emergente
        
        # 3. Ir al carrito desde la barra de navegación superior
        btn_cart = self.driver.find_element(By.ID, "cartur")
        btn_cart.click()
        
        # Validación: Verificar que el producto 'Sony vaio i5' aparezca en la tabla del carrito
        producto_en_carrito = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//td[contains(text(), 'Sony vaio i5')]")))
        self.assertTrue(producto_en_carrito.is_displayed(), "El producto no se encuentra en el carrito.")

    def test_03_proceso_checkout(self):
        """CP-03: Completar proceso de compra en el modal"""
        # 1. Clic en "Place Order" (suponiendo que ya estamos en el carrito por el test anterior)
        btn_place_order = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Place Order']")))
        btn_place_order.click()
        
        # 2. Esperar a que aparezca el modal y llenar el formulario
        self.wait.until(EC.visibility_of_element_located((By.ID, "name"))).send_keys("Usuario de Prueba")
        self.driver.find_element(By.ID, "country").send_keys("Argentina")
        self.driver.find_element(By.ID, "city").send_keys("San Juan")
        self.driver.find_element(By.ID, "card").send_keys("1234567890123456")
        self.driver.find_element(By.ID, "month").send_keys("12")
        self.driver.find_element(By.ID, "year").send_keys("2026")
        
        # 3. Clic en "Purchase"
        btn_purchase = self.driver.find_element(By.XPATH, "//button[text()='Purchase']")
        btn_purchase.click()
        
        # 4. Validación: Demoblaze usa "SweetAlert" para mostrar el éxito de la compra. Validamos ese mensaje.
        mensaje_exito = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".sweet-alert h2")))
        self.assertEqual(mensaje_exito.text, "Thank you for your purchase!", "El mensaje de éxito no coincide.")
        
        # Clic en "OK" para cerrar el modal de éxito
        btn_ok = self.driver.find_element(By.CSS_SELECTOR, ".confirm")
        btn_ok.click()

    @classmethod
    def tearDownClass(cls):
        """Limpieza al finalizar."""
        print("Pruebas finalizadas. Cerrando navegador en 3 segundos...")
        time.sleep(3) # Para que puedas ver cómo termina
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2)