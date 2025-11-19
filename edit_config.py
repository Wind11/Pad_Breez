#!/usr/bin/env python3

import json
import os

CONFIG_FILE = "stalker_config.json"

def load_config():
    """Загружает конфигурацию"""
    default_config = {
        'name': 'STALKER',
        'suit': 'SEVA Suit', 
        'health': 85,
        'radiation': 1250
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return default_config
    except:
        return default_config

def save_config(config):
    """Сохраняет конфигурацию"""
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
        print("✓ Конфигурация сохранена!")
    except Exception as e:
        print(f"✗ Ошибка сохранения: {e}")

def edit_config():
    """Редактирует конфигурацию"""
    config = load_config()
    
    print("╔══════════════════════════════════════╗")
    print("║        РЕДАКТИРОВАНИЕ КОНФИГА       ║")
    print("╠══════════════════════════════════════╣")
    print(f"║ 1. Имя: {config['name']:<26} ║")
    print(f"║ 2. Костюм: {config['suit']:<22} ║")
    print(f"║ 3. Здоровье: {config['health']}%{' ':20} ║")
    print(f"║ 4. Радиация: {config['radiation']}{' ':20} ║")
    print("║ 5. Сохранить и выйти{' ':12} ║")
    print("║ 6. Выход без сохранения{' ':10} ║")
    print("╚══════════════════════════════════════╝")
    
    while True:
        try:
            choice = input("\nВыберите опцию (1-6): ").strip()
            
            if choice == '1':
                new_name = input("Введите новое имя: ").strip()
                if new_name:
                    config['name'] = new_name
                    print(f"✓ Имя изменено на: {new_name}")
            
            elif choice == '2':
                new_suit = input("Введите новый костюм: ").strip()
                if new_suit:
                    config['suit'] = new_suit
                    print(f"✓ Костюм изменен на: {new_suit}")
            
            elif choice == '3':
                try:
                    new_health = int(input("Введите здоровье (0-100): "))
                    if 0 <= new_health <= 100:
                        config['health'] = new_health
                        print(f"✓ Здоровье установлено: {new_health}%")
                    else:
                        print("✗ Ошибка: здоровье должно быть от 0 до 100")
                except ValueError:
                    print("✗ Ошибка: введите число")
            
            elif choice == '4':
                try:
                    new_rad = int(input("Введите радиацию (0-10000): "))
                    if 0 <= new_rad <= 10000:
                        config['radiation'] = new_rad
                        print(f"✓ Радиация установлена: {new_rad}")
                    else:
                        print("✗ Ошибка: радиация должна быть от 0 до 10000")
                except ValueError:
                    print("✗ Ошибка: введите число")
            
            elif choice == '5':
                save_config(config)
                break
            
            elif choice == '6':
                print("Выход без сохранения")
                break
            
            else:
                print("✗ Неверный выбор")
            
            # Показываем обновленную конфигурацию
            print("\nТекущая конфигурация:")
            print(f"  Имя: {config['name']}")
            print(f"  Костюм: {config['suit']}")
            print(f"  Здоровье: {config['health']}%")
            print(f"  Радиация: {config['radiation']}")
            
        except KeyboardInterrupt:
            print("\n\nВыход...")
            break

def quick_set(name=None, suit=None, health=None, radiation=None):
    """Быстрая установка значений через аргументы"""
    config = load_config()
    
    changes = False
    
    if name is not None:
        config['name'] = name
        print(f"✓ Имя установлено: {name}")
        changes = True
    
    if suit is not None:
        config['suit'] = suit
        print(f"✓ Костюм установлен: {suit}")
        changes = True
    
    if health is not None:
        if 0 <= health <= 100:
            config['health'] = health
            print(f"✓ Здоровье установлено: {health}%")
            changes = True
        else:
            print("✗ Ошибка: здоровье должно быть от 0 до 100")
    
    if radiation is not None:
        if 0 <= radiation <= 10000:
            config['radiation'] = radiation
            print(f"✓ Радиация установлена: {radiation}")
            changes = True
        else:
            print("✗ Ошибка: радиация должна быть от 0 до 10000")
    
    if changes:
        save_config(config)
    else:
        print("Текущая конфигурация:")
        print(f"  Имя: {config['name']}")
        print(f"  Костюм: {config['suit']}")
        print(f"  Здоровье: {config['health']}%")
        print(f"  Радиация: {config['radiation']}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        # Интерактивный режим
        edit_config()
    else:
        # Командный режим
        name = None
        suit = None
        health = None
        radiation = None
        
        i = 1
        while i < len(sys.argv):
            if sys.argv[i] == "--name" and i + 1 < len(sys.argv):
                name = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--suit" and i + 1 < len(sys.argv):
                suit = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--health" and i + 1 < len(sys.argv):
                try:
                    health = int(sys.argv[i + 1])
                except ValueError:
                    print("✗ Ошибка: здоровье должно быть числом")
                    sys.exit(1)
                i += 2
            elif sys.argv[i] == "--radiation" and i + 1 < len(sys.argv):
                try:
                    radiation = int(sys.argv[i + 1])
                except ValueError:
                    print("✗ Ошибка: радиация должна быть числом")
                    sys.exit(1)
                i += 2
            else:
                print("Использование:")
                print("  python3 edit_config.py --name 'Имя' --suit 'Костюм' --health 75 --radiation 1500")
                print("  python3 edit_config.py (для интерактивного режима)")
                sys.exit(1)
        
        quick_set(name, suit, health, radiation)
