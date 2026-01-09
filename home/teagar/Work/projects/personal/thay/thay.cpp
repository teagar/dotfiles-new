#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
using namespace std;

const string RESET = "\033[0m";
const string YELLOW = "\033[33;1m"; // Amarelo brilhante

void clearScreen() {
    system("clear");
}

int main() {
    // Frases
    vector<string> frases = {
        "Frase 1: Início do programa",
        "Frase 2: Aprendendo C++",
        "Frase 3: Rolagem no terminal",
        "Frase 4: Exibindo frases",
        "Frase 5: Esta deve ser destacada",
        "Frase 6: Continuando o scroll",
        "Frase 7: Terminal colorido",
        "Frase 8: Quase no fim",
        "Frase 9: Última visível",
        "Frase 10: Extra",
        "Frase 11: Outra",
        "Frase 12: Final"
    };

    // Tempos de exibição (em segundos) para cada frase
    vector<int> tempos = {
        1,  // tempo para frase 1
        2,  // tempo para frase 2
        3,  // tempo para frase 3
        1,  // tempo para frase 4
        4,  // tempo para frase 5
        2,  // tempo para frase 6
        1,  // tempo para frase 7
        2,  // tempo para frase 8
        3,  // tempo para frase 9
        1,  // tempo para frase 10
        2,  // tempo para frase 11
        5   // tempo para frase 12
    };

    int janela = 9; // Quantas frases aparecem por vez

    for (size_t i = 0; i < frases.size(); i++) {
        clearScreen();

        // Mostrar a janela de frases
        for (int j = 0; j < janela; j++) {
            if (i + j < frases.size()) {
                if (j == 4) { // 5ª linha (meio da tela)
                    cout << YELLOW << frases[i + j] << RESET << endl;
                } else {
                    cout << frases[i + j] << endl;
                }
            }
        }

        // Espera o tempo da frase atual antes de rolar
        this_thread::sleep_for(chrono::seconds(tempos[i]));
    }

    return 0;
}
