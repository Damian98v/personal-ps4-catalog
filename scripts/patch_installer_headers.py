"""Apply the bounded native response-header fix to the pinned upstream checkout."""
from pathlib import Path
import sys


def replace(path, old, new):
    text = path.read_text(encoding='utf-8')
    if text.count(old) != 1:
        raise ValueError(f'Expected exactly one upstream match in {path}: {old[:60]}')
    path.write_text(text.replace(old, new), encoding='utf-8')


def apply(root):
    native = root / 'src/http_native.hpp'
    replace(native, 'extern "C" {', '''extern "C" {
int psgiHttpSetResponseHeaderMaxSize(int id, uint64_t bytes) __asm__("sceHttpSetResponseHeaderMaxSize");''')
    http = root / 'src/http.cpp'
    replace(http, '    decltype(&psgiHttpSetAutoRedirect) setAutoRedirect = nullptr;',
            '''    decltype(&psgiHttpSetAutoRedirect) setAutoRedirect = nullptr;
    decltype(&psgiHttpSetResponseHeaderMaxSize) setResponseHeaderMaxSize = nullptr;''')
    replace(http, '        bind(module, "sceHttpSetAutoRedirect", setAutoRedirect);',
            '''        bind(module, "sceHttpSetAutoRedirect", setAutoRedirect);
        bind(module, "sceHttpSetResponseHeaderMaxSize", setResponseHeaderMaxSize);''')
    replace(http, '    check(api.setAutoRedirect(id, 0), "Disable automatic redirects");',
            '''    check(api.setAutoRedirect(id, 0), "Disable automatic redirects");
    // GitHub release redirects exceed the native default response-header buffer.
    // Match the existing bounded redirect parser before any connection is created.
    check(api.setResponseHeaderMaxSize(id, psgi::MaxHttpHeaderBytes), "Set HTTP response header limit");''')

    test = root / 'tests/http_native_test.cpp'
    replace(test, 'size_t offset = 0;', 'size_t offset = 0;\nuint64_t responseHeaderLimit = 5000;')
    replace(test, '    tmpl = true; policy = imageCallback = false; return 4;',
            '    tmpl = true; policy = imageCallback = false; responseHeaderLimit = 5000; return 4;')
    replace(test, 'int psgiHttpSetRecvTimeOut(int id, uint32_t value)', '''int psgiHttpSetResponseHeaderMaxSize(int id, uint64_t value) {
    assert(initialized && tmpl && policy && id == 4 && value == 64 * 1024);
    if (scenario == "header-policy-error") return static_cast<int32_t>(0x804311feu);
    responseHeaderLimit = value;
    return 0;
}
int psgiHttpSetRecvTimeOut(int id, uint32_t value)''')
    replace(test, '    assert(req && id == 6); checkCaLifetime();', '''    assert(req && id == 6); checkCaLifetime();
    if (scenario == "github-headers" && response().headers.size() > responseHeaderLimit)
        return static_cast<int32_t>(0x80431073u);''')
    replace(test, '    RESOLVE("sceHttpSetAutoRedirect", psgiHttpSetAutoRedirect)',
            '''    RESOLVE("sceHttpSetAutoRedirect", psgiHttpSetAutoRedirect)
    RESOLVE("sceHttpSetResponseHeaderMaxSize", psgiHttpSetResponseHeaderMaxSize)''')
    replace(test, '    reset("policy-error");', '''    // Model GitHub's >5 KiB CSP/Location response and a second download hop.
    reset("github-headers");
    const char* release = "https://github.com/fixture/release.pkg";
    const char* asset = "https://release-assets.githubusercontent.com/fixture.pkg";
    responses = {{release, 302, "Content-Security-Policy: " + std::string(6000, 'x') +
                               "\\r\\nLocation: " + asset + "\\r\\n"},
                 {asset, 200, ""}};
    assert(psgi::httpGet(release) == body);
    assert(requestedUrls.size() == 2 && responseHeaderLimit == 64 * 1024);
    reset("header-policy-error");
    rejects([&] { psgi::httpGet(url); }, "Set HTTP response header limit (0x804311FE)");
    reset("policy-error");''')


if __name__ == '__main__':
    apply(Path(sys.argv[1]).resolve())
