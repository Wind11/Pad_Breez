#!/usr/bin/env python3

import os
import time
import json
import sys

CONFIG_FILE = "stalker_config.json"

class StalkerDisplay:
    def __init__(self):
        self.character_data = self.load_config()
    
    def load_config(self):
        """Загружает конфигурацию из файла"""
        default_config = {
            'name': 'STALKER',
            'suit': 'SEVA Suit', 
            'health': 85,
            'radiation': 1250,
            'is_dead': False
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Проверяем что все необходимые поля есть
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    
                    # АВТОМАТИЧЕСКАЯ ПРОВЕРКА СМЕРТИ ПРИ ЗАГРУЗКЕ
                    if config['health'] <= 0 and not config.get('is_dead', False):
                        config['is_dead'] = True
                        config['health'] = 0
                    
                    return config
            else:
                # Создаем файл с настройками по умолчанию
                self.save_config(default_config)
                return default_config
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")
            return default_config    

    def save_config(self, config=None):
        """Сохраняет конфигурацию в файл"""
        if config is None:
            config = self.character_data
        
        # АВТОМАТИЧЕСКАЯ ПРОВЕРКА СМЕРТИ ПЕРЕД СОХРАНЕНИЕМ
        if config['health'] <= 0 and not config.get('is_dead', False):
            config['is_dead'] = True
            config['health'] = 0
            print("💀 Сталкер умер от потери здоровья!")
        elif config['health'] > 0 and config.get('is_dead', False):
            config['is_dead'] = False
            print("✨ Сталкер ожил!")
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения конфига: {e}")
    
    def clear_screen(self):
        os.system('clear')
    
    def draw_progress_bar(self, value, max_value, width=30):
        """Рисует текстовый прогресс-бар"""
        filled = int((value / max_value) * width)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}]"
    
    def format_radiation(self, value):
        if value < 1000:
            return f"{value:>4} R"
        else:
            return f"{value/1000:>5.1f} kR"
    
    def update_display(self):
        # АВТОМАТИЧЕСКАЯ ПРОВЕРКА СМЕРТИ ПЕРЕД ОТОБРАЖЕНИЕМ
        if self.character_data['health'] <= 0 and not self.character_data.get('is_dead', False):
            self.character_data['is_dead'] = True
            self.character_data['health'] = 0
            self.save_config(self.character_data)
            print("💀 Сталкер умер от потери здоровья!")
        
        self.clear_screen()
        
        print("╔══════════════════════════════════════════════╗")
        print("║               STALKER STATUS                ║")
        print("╠══════════════════════════════════════════════╣")
        print(f"║ Name:   {self.character_data['name']:<34} ║")
        print(f"║ Suit:   {self.character_data['suit']:<34} ║")
        
        # Статус смерти
        status = "МЕРТВ" if self.character_data.get('is_dead', False) else "ЖИВ"
        print(f"║ Status:   {status:<34} ║")
        
        print("╠══════════════════════════════════════════════╣")
        
        # Health
        health_bar = self.draw_progress_bar(self.character_data['health'], 100, 25)
        print(f"║ Health:    {self.character_data['health']:>3}% {health_bar} ║")
        
        # Radiation
        rad_text = self.format_radiation(self.character_data['radiation'])
        rad_bar = self.draw_progress_bar(self.character_data['radiation'], 10000, 25)
        print(f"║ Radiation: {rad_text} {rad_bar} ║")
        
        print("╚══════════════════════════════════════════════╝")
        
        # Статусные сообщения
        print("\n" + "═" * 50)
        self.show_status_warnings()
        print("═" * 50)
    
    def show_status_warnings(self):
        """Показывает предупреждения о состоянии"""
        health = self.character_data['health']
        radiation = self.character_data['radiation']
        
        messages = []
        
        # Проверяем смерть
        if self.character_data.get('is_dead', False):
            messages.append("💀 СТАЛКЕР МЕРТВ! Требуется воскрешение!")
        
        if health <= 20:
            messages.append("КРИТИЧЕСКОЕ СОСТОЯНИЕ! Нужна медицинская помощь!")
        elif health <= 50:
            messages.append("Состояние тяжелое, требуется лечение")
        
        if radiation >= 8000:
            messages.append("СМЕРТЕЛЬНЫЙ УРОВЕНЬ РАДИАЦИИ!")
        elif radiation >= 5000:
            messages.append("Высокий уровень радиации, нужны антидоты")
        elif radiation >= 2000:
            messages.append("Повышенный радиационный фон")
        
        if not messages:
            messages.append("Состояние в норме")
        
        for msg in messages:
            print(f"  {msg}")
    
    def run(self):
        """Основной цикл отображения"""
        try:
            while True:
                self.update_display()
                # Обновляем данные из файла каждые 2 секунды
                time.sleep(2)
                self.character_data = self.load_config()
                
        except KeyboardInterrupt:
            print("\nВыход из программы...")

def main():
    try:
        display = StalkerDisplay()
        display.run()
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
