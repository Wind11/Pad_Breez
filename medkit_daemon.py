#!/usr/bin/env python3

import os
import json
import time
import subprocess
from pathlib import Path

CONFIG_FILE = "stalker_config.json"
MEDKIT_USED_FILE = "USED.txt"

# Типы аптечек и их эффекты
MEDKIT_TYPES = {
    "medkit_regular.txt": {  # Обычная аптечка
        "health_restore": 60,
        "radiation_reduce": 10
    },
    "medkit_military.txt": {  # Армейская аптечка
        "health_restore": 100, 
        "radiation_reduce": 10
    },
    "medkit_science.txt": {  # Научная аптечка
        "health_restore": 100,
        "radiation_reduce": 100
    },
    "antidote.txt": {  # Антидот
        "health_restore": 0,
        "radiation_reduce": 100
    },
    "vodka.txt": {  # Водка
        "health_restore": 0, 
        "radiation_reduce": 30
    },
    "ressurect.txt": {  # Воскрешение
        "health_restore": 100,  # Воскрешает с 100% здоровья
        "radiation_reduce": 100,
        "is_ressurect": True  # Флаг воскрешения
    }
}

class MedkitDaemon:
    def __init__(self):
        self.used_medkits = set()
    
    def find_usb_drives(self):
        """Находит все подключенные USB флешки"""
        usb_drives = []
        
        print(f"DEBUG: Checking /media/usb0 - exists: {os.path.exists('/media/usb0')}, ismount: {os.path.ismount('/media/usb0')}")  # ← ДОБАВИТЬ
        
        # Пытаемся смонтировать флешку если устройство есть но не смонтировано
        if os.path.exists('/dev/sda1') and not os.path.ismount('/media/usb0'):
            try:
                print("DEBUG: Attempting to mount /dev/sda1...")
                subprocess.run(['mkdir', '-p', '/media/usb0'], check=True)
                # ИСПОЛЬЗУЕМ SUDO ДЛЯ МОНТИРОВАНИЯ
                result = subprocess.run(['sudo', 'mount', '/dev/sda1', '/media/usb0'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ USB flash drive auto-mounted")
                else:
                    print(f"DEBUG: Mount failed: {result.stderr}")
            except Exception as e:
                print(f"Mount error: {e}")        
        # Проверяем стандартные точки монтирования
        mount_points = [
            "/media/*",
            "/mnt/*", 
            "/run/media/*/*"
        ]
        
        print(f"DEBUG: Checking mount points: {mount_points}")  # ← ДОБАВИТЬ
        
        for pattern in mount_points:
            try:
                from glob import glob
                mounts = glob(pattern)
                print(f"DEBUG: Pattern {pattern} found: {mounts}")  # ← ДОБАВИТЬ
                for mount in mounts:
                    if os.path.ismount(mount) and os.access(mount, os.R_OK):
                        print(f"DEBUG: Checking mount {mount}")  # ← ДОБАВИТЬ
                        if self.is_usb_drive(mount):
                            usb_drives.append(mount)
                            print(f"DEBUG: Added USB drive: {mount}")  # ← ДОБАВИТЬ
            except Exception as e:
                print(f"DEBUG: Error in pattern {pattern}: {e}")  # ← ДОБАВИТЬ
        
        print(f"DEBUG: Final USB drives list: {usb_drives}")  # ← ДОБАВИТЬ
        return usb_drives        
        return usb_drives
    

    def is_usb_drive(self, mount_point):
        """Проверяет, что это USB флешка, а не системный раздел"""
        try:
            # Исключаем системные разделы
            system_mounts = ["/boot", "/efi", "/", "/home", "/var", "/tmp"]
            if mount_point in system_mounts:
                return False
            
            # Проверяем наличие файлов аптечек
            for medkit_file in MEDKIT_TYPES.keys():
                if os.path.exists(os.path.join(mount_point, medkit_file)):
                    return True
            
            return False
        except:
            return False
    
    def check_medkit_on_drive(self, drive_path):
        """Проверяет наличие аптечки на флешке"""
        # Проверяем, не использована ли уже аптечка на этой флешке
        used_file = os.path.join(drive_path, MEDKIT_USED_FILE)
        if os.path.exists(used_file):
            return None
        
        # Ищем файл аптечки
        for medkit_file, effects in MEDKIT_TYPES.items():
            medkit_path = os.path.join(drive_path, medkit_file)
            if os.path.exists(medkit_path):
                return medkit_file, effects, medkit_path
        
        return None
    
    def load_config(self):
        """Загружает конфигурацию персонажа"""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return None
    
    def check_and_update_death_status(self, config):
        """Автоматически проверяет и обновляет статус смерти"""
        if config['health'] <= 0 and not config.get('is_dead', False):
            config['is_dead'] = True
            config['health'] = 0
            print("💀 Сталкер умер от потери здоровья!")
            return True
        elif config['health'] > 0 and config.get('is_dead', False):
            config['is_dead'] = False
            print("✨ Сталкер ожил!")
            return True
        return False

    def save_config(self, config):
        """Сохраняет конфигурацию персонажа"""
        try:
            # АВТОМАТИЧЕСКАЯ ПРОВЕРКА СМЕРТИ ПЕРЕД СОХРАНЕНИЕМ
            death_status_changed = self.check_and_update_death_status(config)
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            if death_status_changed:
                print("📄 Конфиг сохранен с обновленным статусом смерти")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
        
    def mark_medkit_used(self, drive_path, medkit_file):
        """Помечает аптечку как использованную (кроме воскрешения)"""
        # Воскрешение не помечается как использованное
        if medkit_file == "ressurect.txt":
            print("♻️ Воскрешение можно использовать многократно")
            return True
            
        try:
            used_file = os.path.join(drive_path, MEDKIT_USED_FILE)
            
            # Создаем файл
            result = subprocess.run(['sudo', 'touch', used_file], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Ошибка создания USED.txt: {result.stderr}")
                return False
            
            # Синхронизируем
            subprocess.run(['sudo', 'sync', used_file], check=False)
            
            print("✅ Аптечка помечена как использованная")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка пометки аптечки: {e}")
            return False

    def use_medkit_auto(self, medkit_info, drive_path):
        """Автоматически использует аптечку"""
        medkit_file, effects, medkit_path = medkit_info
        
        print(f"🔍 DEBUG: Using {medkit_file}, effects: {effects}")  # ← ДОБАВИТЬ
        
        config = self.load_config()
        if not config:
            return False
        
        is_ressurect = effects.get('is_ressurect', False)
        is_dead = config.get('is_dead', False)
        
        print(f"🔍 DEBUG: is_dead={is_dead}, is_ressurect={is_ressurect}")  # ← ДОБАВИТЬ
        
        # ЛОГИКА СМЕРТИ И ВОСКРЕШЕНИЯ
        if is_dead and not is_ressurect:
            print("💀 Сталкер мертв! Нужно воскрешение.")
            return False
        
        # Если сталкер мертв и это воскрешение - воскрешаем
        if is_dead and is_ressurect:
            config['is_dead'] = False
            config['health'] = 100
            config['radiation'] = 0
            print("✨ Сталкер воскрешен полностью здоровым!")
            health_restored = 100
            radiation_reduced = config['radiation']
        else:
            # Применяем обычные эффекты
            old_health = config['health']
            old_radiation = config['radiation']
            
            config['health'] = min(100, config['health'] + effects['health_restore'])
            health_restored = config['health'] - old_health
            
            radiation_reduce = (effects['radiation_reduce'] / 100) * config['radiation']
            config['radiation'] = max(0, config['radiation'] - radiation_reduce)
            radiation_reduced = old_radiation - config['radiation']
            
            # Проверяем смерть после эффектов
            if config['health'] <= 0:
                config['is_dead'] = True
                config['health'] = 0
                print("💀 Сталкер умер!")
        
        print(f"🔍 DEBUG: Final state - health={config['health']}, radiation={config['radiation']}, is_dead={config.get('is_dead', False)}")  # ← ДОБАВИТЬ
        
        # Сохраняем конфиг
        if not self.save_config(config):
            return False
        
        # Помечаем как использованную (кроме воскрешения)
        if not self.mark_medkit_used(drive_path, medkit_file):
            return False
        
        # ... остальной код логирования ...        
        # Логируем
        medkit_name = {
            "medkit_regular.txt": "Обычная аптечка",
            "medkit_military.txt": "Армейская аптечка", 
            "medkit_science.txt": "Научная аптечка",
            "antidote.txt": "Антидот",
            "vodka.txt": "Водка",
            "ressurect.txt": "Воскрешение"
        }.get(medkit_file, "Неизвестная")
        
        log_message = f"{medkit_name} использована. Здоровье: +{health_restored}%, Радиация: -{radiation_reduced:.1f}"
        
        try:
            with open("medkit_log.txt", "a", encoding='utf-8') as f:
                f.write(f"{time.ctime()}: {log_message}\n")
        except:
            pass
        
        print(f"💊 {log_message}")
        return True
    def run(self):
        """Основной цикл мониторинга"""
        print("Medkit daemon started. Monitoring USB drives...")
        
        while True:
            try:
                # Ищем USB флешки
                usb_drives = self.find_usb_drives()
                print(f"DEBUG: Found {len(usb_drives)} USB drives: {usb_drives}")
                for drive in usb_drives:
                    # Проверяем аптечку на флешке
                    medkit_info = self.check_medkit_on_drive(drive)
                    
                    if medkit_info:
                        # Используем аптечку автоматически
                        if self.use_medkit_auto(medkit_info, drive):
                            print(f"Medkit used from {drive}")
                
                # УВЕЛИЧИМ ЧАСТОТУ ПРОВЕРКИ - ждем только 1 секунду
                time.sleep(1)  # ← ИЗМЕНИТЬ с 2 на 1
                
            except KeyboardInterrupt:
                print("Medkit daemon stopped.")
                break
            except Exception as e:
                print(f"Error in daemon: {e}")
                time.sleep(5)
def main():
    # Запускаем в фоновом режиме
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--foreground":
        daemon = MedkitDaemon()
        daemon.run()
    else:
        # Запускаем в фоне
        import subprocess
        subprocess.Popen([
            sys.executable, __file__, "--foreground"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Medkit daemon started in background.")

if __name__ == "__main__":
    main()
