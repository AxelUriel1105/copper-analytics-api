import re
from playwright.sync_api import sync_playwright

def clean_price(price_str):
    """
    Limpiar y convertir la cadena de texto a un valor flotante.
    Elimina caracteres de moneda, comas y espacios.
    """
    if not price_str:
        return None
    # Eliminar todo lo que no sea dígito o punto decimal
    clean = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
    try:
        return float(clean)
    except ValueError:
        return None

def scrape_iusa(page):
    """
    Navegar a IUSA y extraer el precio del producto.
    Maneja la fragmentación de spans uniendo el texto interno del contenedor.
    """
    url = "https://www.tiendaiusa.com/tubo-rigido-tipo-l-tramo-de-61-m-1-2-308761"
    print(f"[INFO] Iniciando extraccion para IUSA: {url}")
    
    try:
        page.goto(url, timeout=60000)
        
        # Estrategia: Buscar el contenedor padre del precio.
        # En VTEX (plataforma de IUSA), suelen usar clases que contienen 'sellingPriceValue'
        # Playwright unira automaticamente los <span>1</span><span>,</span>... en un solo texto.
        selector = "span[class*='sellingPriceValue']"
        
        # Esperar a que el elemento sea visible en el DOM
        page.wait_for_selector(selector, timeout=15000)
        
        # Obtener el texto completo (innerText une los hijos automaticamente)
        price_text = page.locator(selector).first.inner_text()
        
        price = clean_price(price_text)
        print(f"[SUCCESS] Precio crudo detectado: {price_text}")
        print(f"[SUCCESS] Precio final: {price}")
        
        if price:
            # Calculo por metro (Tramo de 6.1m)
            print(f"[DATA] Precio por metro calculado: {round(price/6.1, 2)}")
            return price

    except Exception as e:
        print(f"[ERROR] Fallo en IUSA: {e}")
        return None

def scrape_sodimac(page):
    """
    Navegar a Sodimac y extraer el precio del producto.
    Maneja selectores dinamicos de React.
    """
    url = "https://www.sodimac.com.mx/sodimac-mx/product/265926/tubo-de-cobre-de-1-2-de-6-metros/265926/"
    print(f"\n[INFO] Iniciando extraccion para SODIMAC: {url}")
    
    try:
        page.goto(url, timeout=60000)
        
        # Estrategia: Evitar clases 'jsx-' ya que son dinamicas.
        # Buscar por atributo 'data-testid' que suele ser estable en pruebas de UI
        # o buscar el H1 del precio si existe.
        
        # Selector primario: ID que suele usar Sodimac para precios principales
        # Intentamos buscar cualquier elemento cuyo ID empiece con 'price-' o testid
        selector = "[data-testid^='price-']"
        
        try:
            page.wait_for_selector(selector, timeout=10000)
            price_text = page.locator(selector).first.inner_text()
        except:
            print("[WARN] Selector primario fallo, intentando busqueda alternativa...")
            # Fallback: Buscar texto que parezca precio cerca del boton de compra
            # Buscamos un div que contenga el simbolo de pesos y este visible
            price_text = page.locator("div:has-text('$')").locator("visible=true").first.inner_text()

        price = clean_price(price_text)
        print(f"[SUCCESS] Precio crudo detectado: {price_text}")
        print(f"[SUCCESS] Precio final: {price}")
        
        if price:
            # Calculo por metro (Tramo de 6.0m)
            print(f"[DATA] Precio por metro calculado: {round(price/6.0, 2)}")
            return price

    except Exception as e:
        print(f"[ERROR] Fallo en SODIMAC: {e}")
        # Captura de pantalla para depuracion
        page.screenshot(path="debug_sodimac_error.png")
        return None

def main():
    """
    Funcion principal que orquesta el navegador y los scrapers.
    """
    with sync_playwright() as p:
        # headless=True para ejecutar sin interfaz grafica (mas rapido y profesional)
        # headless=False si necesitas ver el navegador para depurar
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        scrape_iusa(page)
        scrape_sodimac(page)
        
        browser.close()

if __name__ == "__main__":
    main()