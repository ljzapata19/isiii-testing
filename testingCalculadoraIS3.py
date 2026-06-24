import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- CONFIGURACIÓN DEL TESTING ---
# Cambia este valor para probar distintos builds ("Prototype", "7", "1", etc.)
BUILD_A_PROBAR = "7"  

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

    def test_cp4_division_por_cero(self):
        """CP4: Validar control de división por cero"""
        resultado = self.ejecutar_operacion("10", "0", "Divide")
        self.assertEqual(resultado, "Divide by zero error!", "CP4 Fallido")

    def test_cp5_coma_first_number(self):
        """CP5: Validar rechazo de comas en decimales (First Number)"""
        resultado = self.ejecutar_operacion("10,5", "10", "Add")
        self.assertEqual(resultado, "Number 1 is not a number", "CP5 Fallido")

    def test_cp7_vacio_first_number(self):
        """CP7: Validar comportamiento con First Number vacío"""
        resultado = self.ejecutar_operacion("", "10.6", "Subtract")
        self.assertEqual(resultado, "-10.6", "CP7 Fallido")

    def test_cp8_vacio_second_number(self):
        """CP8: Validar comportamiento con Second Number vacío"""
        resultado = self.ejecutar_operacion("10", "", "Multiply")
        self.assertEqual(resultado, "0", "CP8 Fallido")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculadoraIS3)
    print("\n--- EJECUCIÓN DE PRUEBAS AUTOMATIZADAS ---")
    
    hubo_fallos = False
    
    for test in suite:
        descripcion = test._testMethodDoc or test._testMethodName
        instancia_test = TestCalculadoraIS3(test._testMethodName)
        
        try:
            instancia_test.setUp()
            # Ejecutamos el caso de prueba propiamente dicho
            getattr(instancia_test, test._testMethodName)()
            print(f"{descripcion} ... ok")
        except AssertionError:
            print(f"{descripcion} ... FAIL")
            hubo_fallos = True
        except Exception as e:
            print(f"{descripcion} ... ERROR")
            hubo_fallos = True
        finally:
            try:
                instancia_test.tearDown()
            except Exception:
                pass

    print("-" * 50)
    if not hubo_fallos:
        print("OK")
    else:
        print("FAILED (Hay errores en las pruebas)")
    print("\n")