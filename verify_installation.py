import sys
import subprocess

def check_install():
    print("--- Vérification de l'environnement SmartScheduler ---")
    
    # 1. Vérification de la version Python (Objectif OT4)
    print(f"Python version: {sys.version.split()[0]} - {'OK' if sys.version_info >= (3, 8) else 'TROP ANCIENNE'}")

    # 2. Vérification des bibliothèques Python
    libraries = ['pyDatalog', 'pymzn', 'pytest']
    for lib in libraries:
        try:
            __import__(lib)
            print(f"✓ {lib}: Installé")
        except ImportError:
            print(f"✗ {lib}: MANQUANT (faites 'pip install {lib}')")

    # 3. Vérification de l'accès à MiniZinc (Objectif OT2)
    try:
        # On tente de demander la version à l'exécutable minizinc
        result = subprocess.run(['minizinc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ MiniZinc: Détecté ({result.stdout.splitlines()[0]})")
        else:
            print("✗ MiniZinc: Installé mais erreur lors de l'exécution")
    except FileNotFoundError:
        print("✗ MiniZinc: NON DÉTECTÉ dans le PATH système.")

if __name__ == "__main__":
    check_install()
