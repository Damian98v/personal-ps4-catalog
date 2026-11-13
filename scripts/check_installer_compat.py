"""Compile and run the actual upstream catalog parser at a pinned revision (CI)."""
from pathlib import Path
import subprocess
import tempfile
import urllib.request
from catalog import ROOT

REVISION = 'f9212596bafd1011aec594cd8c5bd0d05cff938a'


def main():
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for path in ['src/catalog.cpp', 'src/catalog.hpp', 'src/metadata.cpp', 'src/metadata.hpp',
                     'src/json.hpp', 'third_party/cjson/cJSON.c', 'third_party/cjson/cJSON.h']:
            url = f'https://raw.githubusercontent.com/e1z0/PS4-Games-Installer/{REVISION}/{path}'
            with urllib.request.urlopen(url, timeout=20) as r:
                data = r.read(1024 * 1024)
            (work / Path(path).name).write_bytes(data)
        (work / 'main.cpp').write_text('''#include "catalog.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
int main(int argc, char** argv) {
  std::ifstream input(argv[1]);
  std::string text((std::istreambuf_iterator<char>(input)), {});
  try {
    auto entries = psgi::parseCatalog(text, "games");
    std::cout << "Upstream PS4 Games Installer accepted " << entries.size() << " packages\\n";
  } catch (const std::exception& e) { std::cerr << e.what(); return 1; }
}
''', encoding='utf-8')
        subprocess.run(['gcc', '-c', 'cJSON.c', '-o', 'cJSON.o'], cwd=work, check=True)
        subprocess.run(['g++', '-std=c++17', 'main.cpp', 'catalog.cpp', 'metadata.cpp',
                        'cJSON.o', '-o', 'compat'], cwd=work, check=True)
        subprocess.run([str(work / 'compat'), str(ROOT / 'games.json')], check=True)


if __name__ == '__main__':
    main()
