<template>
  <div class="p-6 max-w-4xl mx-auto space-y-8">
    <!-- Nagłówek -->
    <div class="border-b border-gray-200 dark:border-custom-border pb-4 transition-colors">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-custom-light">Instrukcja obsługi i konfiguracji</h1>
      <p class="text-gray-600 dark:text-custom-muted mt-1">
        Przewodnik krok po kroku dotyczący rejestracji, parowania sieciowego oraz resetowania modułów ESP32 w systemie.
      </p>
    </div>

    <!-- Sekcja 1: Pierwsze uruchomienie i dodanie urządzenia -->
    <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border transition-colors">
      <h2 class="text-xl font-bold text-gray-800 dark:text-custom-light mb-4 flex items-center gap-2">
        <span class="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 w-8 h-8 rounded-full flex items-center justify-center text-sm">1</span>
        Rejestracja i pierwsze uruchomienie
      </h2>
      <ol class="space-y-4 text-gray-700 dark:text-custom-light list-decimal list-inside ml-2">
        <li>Przejdź do zakładki <strong>Moje urządzenia</strong> i kliknij przycisk <strong>Dodaj urządzenie</strong>.</li>
        <li>Wypełnij formularz konfiguracyjny, podając nazwę węzła pomiarowego, jego lokalizację oraz przypisując docelowy typ uprawy. Opcjonalnie możesz aktywować powiadomienia e-mail o stanach krytycznych.</li>
        <li>Po zatwierdzeniu formularza system wygeneruje <strong>unikalny klucz dostępu (token API)</strong>. Skopiuj go i przechowuj w bezpiecznym miejscu – klucz ten będzie wymagany do uwierzytelnienia mikrokontrolera.</li>
        <li>Umieść źródło zasilania (baterie) w urządzeniu ESP32. Odczekaj chwilę, aż w dostępnych sieciach Wi-Fi pojawi się punkt dostępowy o nazwie <code class="bg-gray-100 dark:bg-custom-dark px-1 py-0.5 rounded border border-gray-200 dark:border-custom-border">Thermometer WIFI</code>.<br>
          <span class="text-sm text-gray-500 dark:text-custom-muted ml-6">Wskazówka: Jeśli sieć nie jest rozgłaszana, wymuś reset sprzętowy, przytrzymując fizyczny przycisk na urządzeniu przez 5 sekund.</span>
        </li>
        <li>Połącz się z utworzoną siecią, używając hasła: <code class="bg-gray-100 dark:bg-custom-dark px-1 py-0.5 rounded border border-gray-200 dark:border-custom-border font-bold">admin1234</code>. Następnie otwórz przeglądarkę internetową i przejdź pod adres <strong>192.168.4.1</strong>.</li>
        <li>W panelu konfiguracyjnym urządzenia podaj nazwę i hasło swojej domowej sieci Wi-Fi oraz wklej wygenerowany wcześniej token API. Po zapisaniu ustawień urządzenie automatycznie się zrestartuje, rozłączy tryb konfiguracji i rozpocznie przesyłanie telemetrii.</li>
      </ol>
    </div>

    <!-- Sekcja 2: Generowanie nowego klucza (Reset połączenia) -->
    <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border transition-colors">
      <h2 class="text-xl font-bold text-gray-800 dark:text-custom-light mb-4 flex items-center gap-2">
        <span class="bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-500 w-8 h-8 rounded-full flex items-center justify-center text-sm">2</span>
        Rotacja kluczy i zmiana sieci Wi-Fi
      </h2>
      <ol class="space-y-4 text-gray-700 dark:text-custom-light list-decimal list-inside ml-2">
        <li>W panelu analitycznym urządzenia przejdź do <strong>Ustawień</strong> i użyj opcji <strong>Wygeneruj nowy token</strong>. Skopiuj nowy klucz (stary natychmiast utraci ważność).</li>
        <li>Przytrzymaj fizyczny przycisk resetu na urządzeniu pomiarowym przez około 3 sekundy, aby zainicjować tryb parowania.</li>
        <li>Odczekaj, aż punkt dostępowy <code class="bg-gray-100 dark:bg-custom-dark px-1 py-0.5 rounded border border-gray-200 dark:border-custom-border">Thermometer WIFI</code> stanie się widoczny, a następnie połącz się z nim (hasło: <code class="bg-gray-100 dark:bg-custom-dark px-1 py-0.5 rounded font-bold border border-gray-200 dark:border-custom-border">admin1234</code>).</li>
        <li>Przejdź pod adres <strong>192.168.4.1</strong> w przeglądarce.</li>
        <li>Uzupełnij formularz poświadczeniami do sieci Wi-Fi oraz wprowadź <strong>nowy token API</strong>. Zatwierdź, aby przywrócić komunikację z serwerem.</li>
      </ol>
    </div>

    <!-- Sekcja 3: Wycofanie urządzenia -->
    <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg border border-red-200 dark:border-red-900/50 transition-colors">
      <h2 class="text-lg font-semibold text-red-800 dark:text-red-500 mb-2 flex items-center gap-2">
        ⚠️ Trwałe usunięcie urządzenia z systemu
      </h2>
      <p class="text-sm text-red-700 dark:text-red-400/90 ml-6">
        Usunięcie urządzenia z poziomu aplikacji webowej natychmiast zrywa jego uprawnienia do przesyłania danych. Aby zachować bezpieczeństwo i zapobiec zbędnemu zużyciu energii przy nieudanych próbach autoryzacji, bezpośrednio po usunięciu modułu z systemu zresetuj go do ustawień fabrycznych (przycisk przez 5 sekund), a jeśli nie planujesz jego ponownego wykorzystania — <strong>wyjmij źródło zasilania (baterie)</strong>.
      </p>
    </div>
  </div>
</template>