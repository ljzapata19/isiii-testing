import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- CONFIGURACIÓN DEL TESTING ---
# Cambia este valor para probar distintos builds ("Prototype", "7", "1", etc.)
BUILD_A_PROBAR = "9"  # Cambia a "7" o "1" según el build que quieras probar

class TestCalculadoraIS3(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.URL_CALCULADORA = "https://gerabarud.github.io/is3-calculadora/" 
        self.driver.get(self.URL_CALCULADORA)
        self.driver.maximize_window()
        
        wait = WebDriverWait(self.driver, 5)
        
        # 1. Seleccionar el Build
        # IMPORTANTE: Presiona F12 en la página y verifica el ID real del 
        # menú desplegable de builds. Aquí asumo que el ID es "build" o "selectBuild".
        # Reemplaza "id-del-selector-de-builds" por el ID correcto.
        select_build_element = wait.until(EC.presence_of_element_located((By.ID, "selectBuild")))
        select_build = Select(select_build_element)
        select_build.select_by_visible_text(BUILD_A_PROBAR)
        
        # Pequeña pausa para permitir que el DOM se actualice tras cambiar de build
        time.sleep(1) 

    def ejecutar_operacion(self, first_num, second_num, operation):
        driver = self.driver
        wait = WebDriverWait(driver, 5)
        
        # 1. Completar First Number
        input_first = wait.until(EC.presence_of_element_located((By.ID, "number1Field")))
        input_first.clear()
        input_first.send_keys(first_num)
        
        # 2. Completar Second Number
        input_second = driver.find_element(By.ID, "number2Field")
        input_second.clear()
        input_second.send_keys(second_num)
        
        # 3. Seleccionar Operación
        select_op = Select(driver.find_element(By.ID, "selectOperationDropdown"))
        select_op.select_by_visible_text(operation)
        
        # 4. Hacer clic en Calculate
        btn_calc = driver.find_element(By.ID, "calculateButton")
        btn_calc.click()
        
        # 5. Pausa táctica de 1.5 segundos para dejar que el JavaScript procese
       # time.sleep(1.5)
        
        # 6. Leemos el campo de errores primero
        resultado_err = driver.find_element(By.ID, "errorMsgField").text
        
        # Si hay un error, devolvemos eso y cortamos acá
        if resultado_err != "":
            return resultado_err
        
        # Si no hay error, buscamos el valor del campo de respuesta numérico.
        # Al no usar EC.visibility_of_element_located, no nos afecta si el Prototipo se cuelga.
        resultado_num = driver.find_element(By.ID, "numberAnswerField").get_attribute("value")
        return resultado_num
        # Recuperar y retornar el resultado
        # resultado_elem = wait.until(EC.visibility_of_element_located((By.ID, "numberAnswerField")))
        # return resultado_elem.get_attribute("value") # Cambiamos .text por .get_attribute("value")

    # --- Ejecución de los Casos de Prueba ---

    def test_cp1_letras_first_number(self):
        """CP1: Validar ingreso de letras en First Number"""
        resultado = self.ejecutar_operacion("h", "17", "Add")
        self.assertEqual(resultado, "Number 1 is not a number", "CP1 Fallido")

    def test_cp2_letras_second_number(self):
        """CP2: Validar ingreso de letras en Second Number"""
        resultado = self.ejecutar_operacion("120", "a", "Add")
        self.assertEqual(resultado, "Number 2 is not a number", "CP2 Fallido")

    def test_cp3_nuevas_operaciones(self):
            """CP3: Probar ingresar nuevas operaciones"""
            # Completamos campos iniciales requeridos según matriz de diseño (10 y 5)
            wait = WebDriverWait(self.driver, 5)
            input_first = wait.until(EC.presence_of_element_located((By.ID, "number1Field")))
            input_first.clear()
            input_first.send_keys("10")
            
            input_second = self.driver.find_element(By.ID, "number2Field")
            input_second.clear()
            input_second.send_keys("5")

            # Capturamos las opciones actuales en la interfaz
            select_op = Select(self.driver.find_element(By.ID, "selectOperationDropdown"))
            opciones_reales = [op.text for op in select_op.options]
            
            # Definimos las que son válidas por requerimiento
            operaciones_validas = {"Add", "Subtract", "Multiply", "Divide", "Concatenate"}
            operaciones_extra = set(opciones_reales) - operaciones_validas
            
            # Si existen elementos no permitidos, falla informando cuáles son
            self.assertEqual(len(operaciones_extra), 0, f"Se encontraron operaciones inválidas: {operaciones_extra}")
    def test_cp4_division_por_cero(self):
        """CP4: Validar control de división por cero"""
        resultado = self.ejecutar_operacion("10", "0", "Divide")
        self.assertEqual(resultado, "Divide by zero error!", "CP4 Fallido")

    def test_cp5_coma_first_number(self):
        """CP5: Validar rechazo de comas en decimales (First Number)"""
        resultado = self.ejecutar_operacion("10,5", "10", "Add")
        self.assertEqual(resultado, "Number 1 is not a number", "CP5 Fallido")
        
    def test_cp6_coma_second_number(self):
        """CP6: Validar rechazo de comas en decimales (Second Number)"""
        resultado = self.ejecutar_operacion("10", "10,5", "Subtract")
        self.assertEqual(resultado, "Number 2 is not a number", "CP6 Fallido")

    def test_cp7_vacio_first_number(self):
        """CP7: Validar comportamiento con First Number vacío"""
        resultado = self.ejecutar_operacion("", "10.6", "Subtract")
        self.assertEqual(resultado, "Number 1 is not a number", "CP7 Fallido")

    def test_cp8_vacio_second_number(self):
        """CP8: Validar comportamiento con Second Number vacío"""
        resultado = self.ejecutar_operacion("10", "", "Multiply")
        self.assertEqual(resultado, "Number 2 is not a number", "CP8 Fallido")

    def tearDown(self):
        self.driver.quit()

# --- EJECUCIÓN DE PRUEBAS AUTOMATIZADAS Y RESUMEN FINAL ---
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculadoraIS3)
    print("\n--- EJECUCIÓN DE PRUEBAS AUTOMATIZADAS ---")
    print(f"Build a probar: {BUILD_A_PROBAR}")
    print("-" * 50)
    
    hubo_fallos = False
    lista_fallas = []
    cantidad_tests_ejecutados = 0
    
    for test in suite:
        descripcion = test._testMethodDoc or test._testMethodName
        id_caso = descripcion.split(":")[0] if ":" in descripcion else test._testMethodName
        instancia_test = TestCalculadoraIS3(test._testMethodName)
        cantidad_tests_ejecutados += 1
        try:
            instancia_test.setUp()
            getattr(instancia_test, test._testMethodName)()
            print(f"{descripcion} ... ok")
        except AssertionError as e:
            print(f"{descripcion} ... FAIL")
            # Imprimimos el detalle del AssertionError con una pequeña sangría
            print(f"    AssertionError: {e}\n")
            hubo_fallos = True
            lista_fallas.append(id_caso)
        except Exception as e:
            print(f"{descripcion} ... ERROR")
            mensaje_limpio = str(e).split("\n")[0]
            print(f"    Error del sistema: {mensaje_limpio}\n")
            hubo_fallos = True
            lista_fallas.append(id_caso)
        finally:
            try:
                instancia_test.tearDown()
            except Exception:
                pass

    print("-" * 50)
    if not hubo_fallos:
        print("OK")
    else:
        casos_rotos = ", ".join(lista_fallas)
        print(f"FAILED (Hay errores en las pruebas)")
        print(f"Casos de prueba que fallaron: {casos_rotos}")
    print(f"Total de pruebas ejecutadas: {cantidad_tests_ejecutados}")
    print("\n")