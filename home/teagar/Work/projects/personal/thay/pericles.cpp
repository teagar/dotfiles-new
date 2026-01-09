#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
using namespace std;

const string RESET   = "\033[0m";
const string YELLOW  = "\033[33;1m";
const string GREEN   = "\033[32;1m";
const string CYAN    = "\033[36;1m";
const string RED     = "\033[31;1m";
const string WHITE   = "\033[37;1m";

struct Line {
    string text;
    string color;
    int timeMs;
};

void clearScreen() {
    system("clear");
}

int main() {
    vector<int> intervals = {
        18907, 3393, 3633, 3710, 3308, 3391, 3551, 3472, 3958, 1776,
        1858, 3470, 1776, 4522, 2504, 3956, 3072, 4521, 4440, 2020,
        3230, 5734, 6462, 3311, 3554, 3794, 3629, 1854, 1856, 3473,
        1777, 4443, 2506, 3878, 3069, 4603, 4361, 2180, 3061, 4516,
        3471, 3148, 2988, 4601, 4440, 1940, 3474, 5658
    };

    vector<Line> lines = {
        {"...", GREEN, intervals[0]},
        {"Tentei fazer valer a pena", GREEN, intervals[1]},
        {"Passei por cima dos problemas", GREEN, intervals[2]},
        {"Achei que eu era o bastante", GREEN, intervals[3]},
        {"Mas não fui pra você", GREEN, intervals[4]},
        {"Tentei ser um cara perfeito", CYAN, intervals[5]},
        {"Eu fiz as coisas do seu jeito", CYAN, intervals[6]},
        {"Queria ser mais importante", CYAN, intervals[7]},
        {"Mas não fui pra você", CYAN, intervals[8]},
        {"Até que durou", YELLOW, intervals[9]},
        {"Me diz o porquê", YELLOW, intervals[10]},
        {"Perdeu tanto tempo aqui", YELLOW, intervals[11]},
        {"Te faço um favor", YELLOW, intervals[12]},
        {"Melhor eu sumir", YELLOW, intervals[13]},
        {"Fui mais um nas suas mãos", RED, intervals[14]},
        {"Não sei se por carência ou falta de opção", RED, intervals[15]},
        {"Só sei que eu senti amor", RED, intervals[16]},
        {"Que pena, só eu senti amor", RED, intervals[17]},
        {"O que faço com os planos dos próximos anos?", RED, intervals[18]},
        {"Juro que não sei", RED, intervals[19]},
        {"Só sei que eu senti amor", RED, intervals[20]},
        {"Que pena, só eu senti amor", RED, intervals[21]},
        {"Só eu senti amor", RED, intervals[22]},
        {"Tentei ser um cara perfeito", CYAN, intervals[23]},
        {"Eu fiz as coisas do seu jeito", CYAN, intervals[24]},
        {"Queria ser mais importante", CYAN, intervals[25]},
        {"Mas não fui pra você", CYAN, intervals[26]},
        {"Até que durou", YELLOW, intervals[27]},
        {"Me diz o porquê", YELLOW, intervals[28]},
        {"Perdeu tanto tempo aqui", YELLOW, intervals[29]},
        {"Te faço um favor", YELLOW, intervals[30]},
        {"Melhor eu sumir", YELLOW, intervals[31]},
        {"Fui mais um nas suas mãos", RED, intervals[32]},
        {"Não sei se por carência ou falta de opção", RED, intervals[33]},
        {"Só sei que eu senti amor", RED, intervals[34]},
        {"Que pena, só eu senti amor", RED, intervals[35]},
        {"O que faço com os planos dos próximos anos?", RED, intervals[36]},
        {"Juro que não sei", RED, intervals[37]},
        {"Só sei que eu senti amor", RED, intervals[38]},
        {"Que pena, só eu senti amor", RED, intervals[39]},
        {"Fui mais um nas suas mãos", RED, intervals[40]},
        {"Não sei se por carência ou falta de opção", RED, intervals[41]},
        {"Só sei que eu senti amor", RED, intervals[42]},
        {"Que pena, só eu senti amor", RED, intervals[43]},
        {"O que faço com os planos dos próximos anos?", RED, intervals[44]},
        {"Juro que não sei", RED, intervals[45]},
        {"Só sei que eu senti amor", RED, intervals[46]},
        {"Que pena, só eu senti amor", RED, intervals[47]},
        {"Só eu (só eu) senti amor", RED, intervals[47]}
    };

    int window = 9;
    int total = lines.size();

    for (int i = 0; i < total; i++) {
        clearScreen();

        int start, end;
        if (i < 4) {
            start = 0;
            end = min(window, total);
        } else if (i > total - 5) {
            end = total;
            start = max(0, end - window);
        } else {
            start = i - 4;
            end = start + window;
            if (end > total) end = total;
        }

        for (int j = start; j < end; j++) {
            bool highlight = false;
            if (i < 4) {
                if (j == i) highlight = true;
            } else if (i > total - 5) {
                if (j == i) highlight = true;
            } else {
                if (j == start + 4) highlight = true;
            }

            if (highlight)
                cout << lines[j].color << lines[j].text << RESET << endl;
            else
                cout << lines[j].text << endl;
        }

        this_thread::sleep_for(chrono::milliseconds(lines[i].timeMs));
    }

    return 0;
}
