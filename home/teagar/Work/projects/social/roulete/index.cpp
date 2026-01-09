// roleta.cpp
// Requisitos: SFML (graphics, window, audio), nlohmann::json (single header).
// Compilar (Linux):
// g++ -std=c++17 roleta.cpp -o roleta -lsfml-graphics -lsfml-window -lsfml-system -lsfml-audio
//
// Estrutura de pastas esperada:
// ./index (executável)
// ./cities.json (opcional: seu arquivo com todas as cidades, formato [{ "name":"Cidade", "state":"UF" }, ...])
// ./assets/flags/<UF>.png  (ex: assets/flags/MG.png)  -> para usar bandeiras dos estados
// ./assets/tick.wav  -> som curto para tick (opcional)
//
// Uso em tempo de execução:
// - Espaço: iniciar sequência de giros (spins)
// - G: girar apenas 1 giro
// - S: alterna som
// - P: alterna física (ease)
// - Up/Down: aumenta/diminui quantidade removida por vez
// - Left/Right: aumenta/diminui número de giros na sequência
// - R: resetar removidos (apaga cidades_removidas.json)
// - E: exportar arquivo cidades_removidas_export.json
//
// Persistência: salva em cidades_removidas.json no diretório atual.

#include <SFML/Graphics.hpp>
#include <SFML/Audio.hpp>
#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <cmath>
#include <filesystem>
#include <random>
#include <algorithm>
#include <string>
#include <sstream>


#include "json.hpp" // nlohmann::json (baixar: https://github.com/nlohmann/json single header -> json.hpp)

using json = nlohmann::json;
namespace fs = std::filesystem;

struct City {
    std::string name;
    std::string state;
};

struct RemovedEntry {
    std::string name;
    std::string state;
};

static std::string REMOVED_FILE = "cidades_removidas.json";
static std::string CITIES_FILE = "cities.json";
static std::string FLAGS_DIR = "assets/flags/";
static std::string TICK_FILE = "assets/tick.wav";

// Configuráveis (podem ser alterados por teclas)
int CONFIG_REMOVE_COUNT = 10;
int CONFIG_SPINS = 6;
bool CONFIG_SOUND = true;
bool CONFIG_PHYSICS = true;

// Funções utilitárias
std::vector<City> loadCitiesFromFile(const std::string &path) {
    std::vector<City> out;
    if (!fs::exists(path)) {
        std::cout << "[info] arquivo cities.json não encontrado, carregando amostra.\n";
        return out;
    }
    std::ifstream ifs(path);
    if (!ifs.is_open()) return out;
    json j;
    try {
        ifs >> j;
        for (auto &it : j) {
            City c;
            c.name = it.value("name", "");
            c.state = it.value("state", "");
            if (!c.name.empty()) out.push_back(c);
        }
    } catch (...) {
        std::cerr << "[erro] JSON inválido em " << path << "\n";
    }
    return out;
}

std::vector<RemovedEntry> loadRemovedFromFile() {
    std::vector<RemovedEntry> out;
    if (!fs::exists(REMOVED_FILE)) return out;
    std::ifstream ifs(REMOVED_FILE);
    if (!ifs.is_open()) return out;
    json j;
    try {
        ifs >> j;
        for (auto &it : j) {
            RemovedEntry r;
            r.name = it.value("name", "");
            r.state = it.value("state", "");
            if (!r.name.empty()) out.push_back(r);
        }
    } catch (...) {
        std::cerr << "[erro] JSON inválido em " << REMOVED_FILE << "\n";
    }
    return out;
}

void saveRemovedToFile(const std::vector<RemovedEntry> &removed) {
    json j = json::array();
    for (auto &r : removed) {
        j.push_back({ {"name", r.name}, {"state", r.state} });
    }
    std::ofstream ofs(REMOVED_FILE);
    ofs << j.dump(2);
    ofs.close();
}

// gera uma cor HSL-like baseada na sigla do estado (fácil, determinística)
sf::Color stateColor(const std::string &s) {
    unsigned int h = 0;
    for (char c : s) h = h * 31 + (unsigned char)c;
    int hue = h % 360;
    // converter hue -> RGB aproximado (simples)
    float H = hue / 60.0f;
    float X = 1.0f - fabs(fmod(H, 2.0f) - 1.0f);
    float r=0,g=0,b=0;
    int hi = int(H);
    switch (hi) {
        case 0: r=1; g=X; b=0; break;
        case 1: r=X; g=1; b=0; break;
        case 2: r=0; g=1; b=X; break;
        case 3: r=0; g=X; b=1; break;
        case 4: r=X; g=0; b=1; break;
        default: r=1; g=0; b=X; break;
    }
    // saturação e lightness
    float sat = 0.65f, light = 0.55f;
    r = r*sat + (1.0f - sat)*light;
    g = g*sat + (1.0f - sat)*light;
    b = b*sat + (1.0f - sat)*light;
    return sf::Color(
        static_cast<sf::Uint8>(std::clamp(r*255.0f,0.0f,255.0f)),
        static_cast<sf::Uint8>(std::clamp(g*255.0f,0.0f,255.0f)),
        static_cast<sf::Uint8>(std::clamp(b*255.0f,0.0f,255.0f))
    );
}

// Agrupa cidades por estado criando blocos contíguos na roleta.
// Retorna um vetor de pares (state, vector<City>)
std::vector<std::pair<std::string, std::vector<City>>> groupByStatePreserveOrder(const std::vector<City>& cities) {
    // Para que blocos por estado fiquem contíguos, vamos agrupar por state
    std::map<std::string, std::vector<City>> m;
    for (auto &c : cities) m[c.state].push_back(c);
    std::vector<std::pair<std::string, std::vector<City>>> out;
    for (auto &p : m) out.push_back(p);
    return out;
}

// Easing
float easeOutCubic(float t) {
    t = std::clamp(t, 0.0f, 1.0f);
    return 1.0f - pow(1.0f - t, 3.0f);
}

int main() {
    // Carrega cidades (se existir)
    std::vector<City> allCities = loadCitiesFromFile(CITIES_FILE);
    if (allCities.empty()) {
        // gerar pequenas amostras se não houver arquivo
        allCities = {
            {"Belo Horizonte","MG"}, {"Uberlândia","MG"}, {"Contagem","MG"},
            {"São Paulo","SP"}, {"Campinas","SP"}, {"Santos","SP"},
            {"Rio de Janeiro","RJ"}, {"Niterói","RJ"},
            {"Curitiba","PR"}, {"Londrina","PR"},
            {"Fortaleza","CE"}, {"Recife","PE"},
            {"Salvador","BA"}, {"Porto Alegre","RS"}
        };
    }

    // Carrega removidos já persistidos
    std::vector<RemovedEntry> removed = loadRemovedFromFile();
    // Filtra as cidades para remover as já retiradas
    auto itFilter = std::remove_if(allCities.begin(), allCities.end(), [&](const City &c){
        for (auto &r : removed) if (r.name == c.name) return true;
        return false;
    });
    allCities.erase(itFilter, allCities.end());

    // Agrupar por estado para formar blocos
    auto grouped = groupByStatePreserveOrder(allCities);

    // Cria uma lista de setores (cada cidade é um setor, mas estados ficam em blocos)
    std::vector<std::pair<City, std::string>> sectors; // pair(city, state)
    for (auto &g : grouped) {
        for (auto &c : g.second) sectors.push_back({c, g.first});
    }

    // Carregar bandeiras (por state)
    std::map<std::string, sf::Texture> flagTextures;
    for (auto &g : grouped) {
        std::string uf = g.first;
        std::string path = FLAGS_DIR + uf + ".png";
        if (fs::exists(path)) {
            sf::Texture tex;
            if (tex.loadFromFile(path)) {
                flagTextures[uf] = tex;
            }
        }
    }

    // carregar tick sound
    sf::SoundBuffer tickBuffer;
    bool haveTick = false;
    if (fs::exists(TICK_FILE)) {
        if (tickBuffer.loadFromFile(TICK_FILE)) haveTick = true;
    }
    sf::Sound tickSound;
    if (haveTick) tickSound.setBuffer(tickBuffer);

    // Janela
    int winW = 1000, winH = 800;
    sf::RenderWindow window(sf::VideoMode(winW, winH), "Roleta de Cidades (C++)");
    window.setFramerateLimit(60);

    // Fonte para texto (usar fonte do sistema se disponível ou incluir uma)
    sf::Font font;
    if (!font.loadFromFile("assets/Roboto-Regular.ttf")) {
        // fallback: usar a fonte padrão SFML não garante – UI ficará sem
        std::cerr << "[warn] fonte assets/Roboto-Regular.ttf não encontrada. Textos podem ficar sem render.\n";
    }

    // Estado do jogo
    float wheelRotation = 0.0f; // radianos
    bool isSpinning = false;
    int currentSpinIndex = 0;

    std::mt19937 rng(std::random_device{}());

    auto drawWheel = [&](sf::RenderTarget &rt) {
        // centro e raio
        float cx = winW * 0.35f;
        float cy = winH * 0.5f;
        float radius = std::min(winW, winH) * 0.35f;

        int total = (int)sectors.size();
        if (total == 0) return;

        float anglePer = 2.0f * M_PI / float(total);

        // desenhar setores por bloco de estado (para cobrir um bloco com a mesma bandeira)
        // Primeiro construir um vetor de blocos: state -> startIndex, count
        struct Block { std::string state; int start; int count; };
        std::vector<Block> blocks;
        if (total>0) {
            int idx = 0;
            while (idx < total) {
                std::string st = sectors[idx].second;
                int cnt = 1;
                int j = idx+1;
                while (j < total && sectors[j].second == st) { cnt++; j++; }
                blocks.push_back({st, idx, cnt});
                idx = j;
            }
        }

        // desenha cada bloco: preencher o arco com cor e tentar desenhar bandeira no centro angular do bloco
        for (auto &b : blocks) {
            int startI = b.start;
            int cnt = b.count;
            float startAngle = wheelRotation + (startI * anglePer) - M_PI/2.0f;
            float endAngle = startAngle + cnt * anglePer;

            // construir um shape triangular approximado (polígono em arco)
            sf::ConvexShape poly;
            int steps = std::max(6, cnt*2); // melhor resolução para blocos grandes
            poly.setPointCount(steps + 2);
            poly.setPoint(0, sf::Vector2f(cx, cy));
            for (int s = 0; s <= steps; ++s) {
                float t = float(s)/float(steps);
                float a = startAngle + t*(endAngle - startAngle);
                float x = cx + cos(a) * radius;
                float y = cy + sin(a) * radius;
                poly.setPoint(s+1, sf::Vector2f(x,y));
            }
            poly.setFillColor(stateColor(b.state));
            poly.setOutlineThickness(1.0f);
            poly.setOutlineColor(sf::Color(0,0,0,80));
            rt.draw(poly);

            // desenhar bandeira do estado sobre o arco (se existir)
            auto it = flagTextures.find(b.state);
            if (it != flagTextures.end()) {
                // calculamos um bounding box aproximado para o arco: centro angular do bloco -> colocar a bandeira nesse angulo
                float midAngle = (startAngle + endAngle) * 0.5f;
                float bx = cx + cos(midAngle) * (radius * 0.45f);
                float by = cy + sin(midAngle) * (radius * 0.45f);
                sf::Sprite spr(it->second);
                // escala para caber
                float maxW = radius * (endAngle - startAngle) * 0.45f; // largura proporcional ao arco
                float maxH = radius * 0.5f;
                float sx = maxW / spr.getLocalBounds().width;
                float sy = maxH / spr.getLocalBounds().height;
                float smin = std::min(sx, sy);
                spr.setScale(smin, smin);
                spr.setOrigin(spr.getLocalBounds().width*0.5f, spr.getLocalBounds().height*0.5f);
                spr.setPosition(bx, by);
                spr.setColor(sf::Color(255,255,255,220));
                rt.draw(spr);
            }
        }

        // Desenhar linhas divisórias e nomes (cada cidade)
        for (int i = 0; i < total; ++i) {
            float sa = wheelRotation + i*anglePer - M_PI/2.0f;
            float ea = sa + anglePer;
            float mid = (sa + ea) * 0.5f;
            // linha de divisão
            sf::VertexArray line(sf::Lines, 2);
            line[0].position = sf::Vector2f(cx, cy);
            line[1].position = sf::Vector2f(cx + cos(sa)*radius, cy + sin(sa)*radius);
            line[0].color = sf::Color(0,0,0,60);
            line[1].color = sf::Color(0,0,0,60);
            rt.draw(line);

            // texto do nome (apenas parte para caber)
            sf::Text txt;
            if (font.getInfo().family.size()) {
                txt.setFont(font);
            }
            txt.setCharacterSize(14);
            std::string name = sectors[i].first.name;
            // reduzir nome se muito longo
            if (name.size()>22) name = name.substr(0,19) + "...";
            txt.setString(name);
            txt.setFillColor(sf::Color::White);
            // posição no meio do setor
            float tx = cx + cos(mid) * (radius - 30);
            float ty = cy + sin(mid) * (radius - 30);
            txt.setPosition(tx - txt.getLocalBounds().width/2.0f, ty - txt.getLocalBounds().height/2.0f);
            // rotacionar para ficar legível? vamos desenhar sem rotação por simplicidade
            rt.draw(txt);
        }

        // centro escuro
        sf::CircleShape center(radius*0.18f);
        center.setOrigin(center.getRadius(), center.getRadius());
        center.setPosition(cx, cy);
        center.setFillColor(sf::Color(20,20,20,220));
        rt.draw(center);

        // ponteiro no topo
        sf::ConvexShape pointer;
        pointer.setPointCount(3);
        pointer.setPoint(0, sf::Vector2f(cx, cy - radius - 12));
        pointer.setPoint(1, sf::Vector2f(cx - 16, cy - radius + 16));
        pointer.setPoint(2, sf::Vector2f(cx + 16, cy - radius + 16));
        pointer.setFillColor(sf::Color(255, 221, 87));
        rt.draw(pointer);
    };

    // Função para tocar tick quando passando por setor
    auto playTick = [&](){
        if (!CONFIG_SOUND) return;
        if (haveTick) tickSound.play();
    };

    // Função que roda a animação de um giro simples (promise-like com callback)
    auto runSingleSpinAnimation = [&](std::function<void()> after) {
        if (sectors.empty()) { if(after) after(); return; }
        isSpinning = true;
        // duração e velocidade variáveis
        float duration = CONFIG_PHYSICS ? (1.2f + (float)(rng()%1200)/1000.0f) : (0.7f + (float)(rng()%400)/1000.0f);
        float initialVel = 6.0f + (rng()%600)/100.0f; // rad/s approx
        float startRot = wheelRotation;
        float startTime = static_cast<float>(clock())/CLOCKS_PER_SEC;
        int total = (int)sectors.size();
        int lastIndex = -1;

        // loop de animação bloqueante (simplifica a lógica): vamos rodar enquanto a janela estiver aberta
        sf::Clock clk;
        while (clk.getElapsedTime().asSeconds() < duration) {
            float t = clk.getElapsedTime().asSeconds() / duration;
            float e = easeOutCubic(t);
            float angle = initialVel * (1.0f - e) * 0.6f; // reduzir amplitude
            wheelRotation += angle * (1.0f/60.0f);
            // tocar tick quando passar setor
            int idx = 0;
            if (!sectors.empty()) {
                float anglePer = 2.0f * M_PI / float(total);
                float normalized = fmod(wheelRotation + M_PI/2.0f + 100.0f*M_PI, 2.0f*M_PI);
                if (normalized < 0) normalized += 2.0f*M_PI;
                idx = int(normalized / anglePer) % total;
            }
            if (idx != lastIndex) {
                lastIndex = idx;
                playTick();
            }

            // processar eventos e desenhar
            sf::Event ev;
            while (window.pollEvent(ev)) {
                if (ev.type == sf::Event::Closed) {
                    saveRemovedToFile(removed);
                    window.close();
                    return;
                }
            }
            window.clear(sf::Color(30,30,40));
            drawWheel(window);
            // HUD
            sf::Text hud;
            if (font.getInfo().family.size()) hud.setFont(font);
            hud.setCharacterSize(16);
            std::ostringstream ss;
            ss << "Cidades na roleta: " << sectors.size() << " | Removidas: " << removed.size() << " | Remove por vez: " << CONFIG_REMOVE_COUNT << " | Spins: " << CONFIG_SPINS
               << " | Som: " << (CONFIG_SOUND? "ON":"OFF") << " | Física: " << (CONFIG_PHYSICS? "ON":"OFF");
            hud.setString(ss.str());
            hud.setFillColor(sf::Color::White);
            hud.setPosition(20,20);
            window.draw(hud);
            window.display();
        }
        isSpinning = false;
        if (after) after();
    };

    // remove N cidades na posição do ponteiro (topo)
    auto removeTopCities = [&](int n) {
        int total = (int)sectors.size();
        if (total == 0) return;
        // determinar índice do setor apontado pela seta (topo)
        float anglePer = 2.0f * M_PI / float(total);
        float angleToFind = -wheelRotation + M_PI/2.0f; // ângulo correspondente ao topo
        // normalizar
        float norm = fmod(angleToFind, 2.0f*M_PI);
        if (norm < 0) norm += 2.0f*M_PI;
        int idx = int(norm / anglePer) % total;
        // selecionar n cidades a partir desse índice (em ordem)
        std::vector<int> indices;
        for (int i = 0; i < n && !sectors.empty(); ++i) {
            indices.push_back((idx + i) % (int)sectors.size());
        }
        // coletar removidos
        std::vector<RemovedEntry> toAdd;
        for (int i = 0; i < (int)indices.size(); ++i) {
            int ind = indices[i];
            toAdd.push_back({sectors[ind].first.name, sectors[ind].first.state});
        }
        // remover do vetor (fazer em ordem decrescente de índice)
        std::sort(indices.begin(), indices.end(), std::greater<int>());
        for (int id : indices) {
            sectors.erase(sectors.begin() + id);
        }
        // adicionar ao removed e salvar
        for (auto &r : toAdd) removed.push_back(r);
        saveRemovedToFile(removed);
    };

    // loop principal
    while (window.isOpen()) {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) {
                saveRemovedToFile(removed);
                window.close();
            } else if (event.type == sf::Event::KeyPressed) {
                if (event.key.code == sf::Keyboard::Space) {
                    if (!isSpinning) {
                        // sequência de giros
                        isSpinning = true;
                        for (int s = 0; s < CONFIG_SPINS; ++s) {
                            // animação e após anim remoção
                            runSingleSpinAnimation([&](){});
                            // após o spin, remover CONFIG_REMOVE_COUNT
                            removeTopCities(CONFIG_REMOVE_COUNT);
                            if (sectors.empty()) break;
                        }
                        isSpinning = false;
                    }
                } else if (event.key.code == sf::Keyboard::G) {
                    if (!isSpinning) {
                        runSingleSpinAnimation([&](){});
                    }
                } else if (event.key.code == sf::Keyboard::S) {
                    CONFIG_SOUND = !CONFIG_SOUND;
                } else if (event.key.code == sf::Keyboard::P) {
                    CONFIG_PHYSICS = !CONFIG_PHYSICS;
                } else if (event.key.code == sf::Keyboard::Up) {
                    CONFIG_REMOVE_COUNT = std::min(100, CONFIG_REMOVE_COUNT + 1);
                } else if (event.key.code == sf::Keyboard::Down) {
                    CONFIG_REMOVE_COUNT = std::max(1, CONFIG_REMOVE_COUNT - 1);
                } else if (event.key.code == sf::Keyboard::Right) {
                    CONFIG_SPINS = std::min(50, CONFIG_SPINS + 1);
                } else if (event.key.code == sf::Keyboard::Left) {
                    CONFIG_SPINS = std::max(1, CONFIG_SPINS - 1);
                } else if (event.key.code == sf::Keyboard::R) {
                    // reset removidos
                    removed.clear();
                    if (fs::exists(REMOVED_FILE)) fs::remove(REMOVED_FILE);
                    // recarregar cidades do arquivo (se houver) ou amostra
                    auto all = loadCitiesFromFile(CITIES_FILE);
                    if (all.empty()) {
                        all = {
                            {"Belo Horizonte","MG"}, {"Uberlândia","MG"}, {"Contagem","MG"},
                            {"São Paulo","SP"}, {"Campinas","SP"}, {"Santos","SP"},
                            {"Rio de Janeiro","RJ"}, {"Niterói","RJ"},
                            {"Curitiba","PR"}, {"Londrina","PR"},
                            {"Fortaleza","CE"}, {"Recife","PE"},
                            {"Salvador","BA"}, {"Porto Alegre","RS"}
                        };
                    }
                    // reagrupar e reconstruir sectors
                    auto g2 = groupByStatePreserveOrder(all);
                    sectors.clear();
                    for (auto &gg : g2) for (auto &c : gg.second) sectors.push_back({c, gg.first});
                    // recarregar flags
                    flagTextures.clear();
                    for (auto &gg : g2) {
                        std::string uf = gg.first;
                        std::string path = FLAGS_DIR + uf + ".png";
                        if (fs::exists(path)) {
                            sf::Texture tex;
                            if (tex.loadFromFile(path)) flagTextures[uf] = tex;
                        }
                    }
                } else if (event.key.code == sf::Keyboard::E) {
                    // exportar arquivo removidos para outro nome
                    json j = json::array();
                    for (auto &r : removed) j.push_back({ {"name", r.name}, {"state", r.state} });
                    std::ofstream ofs("cidades_removidas_export.json");
                    ofs << j.dump(2);
                    ofs.close();
                    std::cout << "[info] exportado cidades_removidas_export.json\n";
                }
            }
        }

        window.clear(sf::Color(30,30,40));
        drawWheel(window);

        // HUD
        sf::Text hud, hint;
        if (font.getInfo().family.size()) {
            hud.setFont(font);
            hint.setFont(font);
        }
        hud.setCharacterSize(16);
        std::ostringstream ss;
        ss << "Cidades: " << sectors.size() << " | Removidas: " << removed.size();
        hud.setString(ss.str());
        hud.setFillColor(sf::Color::White);
        hud.setPosition(20, 20);
        window.draw(hud);

        hint.setCharacterSize(14);
        std::ostringstream sh;
        sh << "[Space] Girar sequência (" << CONFIG_SPINS << "x)   [Up/Down] Remove por vez: " << CONFIG_REMOVE_COUNT
           << "   [S] Som: " << (CONFIG_SOUND?"ON":"OFF") << "   [P] Física: " << (CONFIG_PHYSICS?"ON":"OFF")
           << "   [R] Reset removidos   [E] Exportar";
        hint.setString(sh.str());
        hint.setFillColor(sf::Color(220,220,220));
        hint.setPosition(20, winH - 40);
        window.draw(hint);

        window.display();
    }

    // salvar antes de sair
    saveRemovedToFile(removed);
    return 0;
}
