from flystim.launch import launch
from flystim.screen import Screen

def main():
    screens = [Screen(fullscreen=False)]
    launch(screens=screens, port=62632)

if __name__ == '__main__':
    main()