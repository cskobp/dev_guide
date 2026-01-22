# 編譯 KataGo
KataGo 是用 C++ 寫的。它應該可以在 Linux 或 OSX 上透過支援至少 C++14 的 g++ 編譯，或在 Windows 上透過 MSVC 15 (2017) 及更高版本或 MinGW 編譯。其他編譯器和系統尚未經過測試。如果您想自己執行完整的 KataGo 自我對弈訓練迴圈和/或做自己的研究和實驗，或者如果您想在沒有提供預編譯執行檔的作業系統上執行 KataGo，建議您這麼做。

### 為分散式訓練建置
正如在下面的說明中提到的，但為了醒目而在此重複，如果您建置 KataGo 的目的是為了在 https://katagotraining.org 上用於分散式訓練，請記住：
* 您需要指定 `-DBUILD_DISTRIBUTED=1` 或 `BUILD_DISTRIBUTED` 並安裝 OpenSSL。
* 建置需要在 KataGo repo 的 Git clone 內進行，而不是原始碼的壓縮副本（例如您可能從打包發布下載的）。
* 版本需要支援分散式訓練。**`master` 分支將無法運作** - 請改用最新的發布標籤 (release tag) 或 `stable` 分支的頂端，這兩者應該都可以運作。
* 請**不要**嘗試繞過任何版本控制或安全檢查 - 如果您覺得需要這樣做，請先透過開啟 issue 或在 [discord](https://discord.gg/bqkZAz3) 中傳訊息聯繫。如果您正在進行 KataGo 開發或想要更自由地測試，有一個替代網站 [test.katagodistributed.org](test.katagodistributed.org) 可以使用，請在 discord 的 KataGo 頻道詢問以設定測試帳號。

## Linux
   * 懶人包 (如果您有可用的 GPU):
     ```
     git clone https://github.com/lightvector/KataGo.git
     cd KataGo/cpp
     # 如果您遇到缺少函式庫的錯誤，請使用您的系統套件管理員安裝適當的套件並重試。
     # -DBUILD_DISTRIBUTED=1 只有在您想回貢獻於公開訓練時才需要。
     cmake . -DUSE_BACKEND=OPENCL -DBUILD_DISTRIBUTED=1
     make -j 4
     ```
   * 懶人包 (建置緩慢的純 CPU 版本):
     ```
     git clone https://github.com/lightvector/KataGo.git
     cd KataGo/cpp
     # 如果您遇到缺少函式庫的錯誤，請使用您的系統套件管理員安裝適當的套件並重試。
     cmake . -DUSE_BACKEND=EIGEN -DUSE_AVX2=1
     make -j 4
     ```
   * 需求
      * 最低版本為 3.18.2 的 CMake - 例如在 Debian 上 `sudo apt install cmake`，如果那沒有提供足夠新的版本，則從 https://cmake.org/download/ 下載。
      * 支援至少 C++14 的某個版本的 g++。
      * 如果使用 OpenCL 後端，需要支援 OpenCL 1.2 或更高版本的現代 GPU，或者像[這個](https://software.intel.com/en-us/opencl-sdk)用於 CPU 的東西。但如果使用 CPU，Eigen 應該會更好。
      * 如果使用 CUDA 後端，需要 CUDA 11 或更高版本，以及基於您的 CUDA 版本的相容 CUDNN 版本 (https://developer.nvidia.com/cuda-toolkit) (https://developer.nvidia.com/cudnn) 和支援它們的 GPU。
      * 如果使用 TensorRT 後端，除了相容的 CUDA Toolkit (https://developer.nvidia.com/cuda-toolkit) 之外，您還需要至少 8.5 版的 TensorRT (https://developer.nvidia.com/tensorrt)。
      * 如果使用 Eigen 後端，需要 Eigen3。使用 Debian 套件（即 apt 或 apt-get），這應該是 `libeigen3-dev`。
      * zlib, libzip。使用 Debian 套件（即 apt 或 apt-get），這應該是 `zlib1g-dev`, `libzip-dev`。
      * 如果您想進行自我對弈訓練和研究，可能需要 Google perftools `libgoogle-perftools-dev` 用於 TCMalloc 或其他更好的 malloc 實作。由於未知原因，在具有大量執行緒和平行對局的自我對弈中的分配模式會導致 glibc malloc 下產生大量記憶體碎片，最終耗盡機器的記憶體，但更好的 mallocs 可以很好地處理這個問題。
      * 如果編譯以貢獻於公開分散式訓練，需要 OpenSSL (`libssl-dev`)。
   * Clone 此 repo:
      * `git clone https://github.com/lightvector/KataGo.git`
   * 在 cpp 目錄中使用 CMake 和 make 編譯：
      * `cd KataGo/cpp`
      * `cmake . -DUSE_BACKEND=OPENCL` 或 `cmake . -DUSE_BACKEND=CUDA` 或 `cmake . -DUSE_BACKEND=TENSORRT` 或 `cmake . -DUSE_BACKEND=EIGEN` 取決於您想要哪個後端。
         * 如果使用 TCMalloc，也要指定 `-DUSE_TCMALLOC=1`。
         * 編譯也會呼叫 git 指令將 git hash 嵌入到編譯出的執行檔中，如果這對您造成問題，請指定 `-DNO_GIT_REVISION=1` 來停用它。
         * 指定 `-DUSE_AVX2=1` 以使用 AVX2 和 FMA 支援來編譯 Eigen，這將使其與舊 CPU 不相容，但快得多。（如果您想更進一步，您也可以新增 `-DCMAKE_CXX_FLAGS='-march=native'`，這將專門針對您機器的 CPU 進行最佳化，但執行檔可能根本無法在其他機器上執行）。
         * 指定 `-DBUILD_DISTRIBUTED=1` 以支援貢獻資料給公開分散式訓練。
            * 如果建置分散式版本，您也需要建置支援 Git revision，包括在 repo 的 clone 內建置，而不是僅僅是其原始碼的解壓縮副本。
            * 只有特定標籤版本或分支的建置才能貢獻，特別是，不要使用 `master` 分支，請使用最新的 [release](https://github.com/lightvector/KataGo/releases) 標籤或 `stable` 分支的頂端。為了將任何資料不相容或 Bug 的機會降至最低，請不要嘗試使用自訂更改進行貢獻或繞過這些限制。
      * `make`
   * 完成！您現在應該在您的工作目錄中有一個編譯好的 `katago` 執行檔。
   * 預先訓練的類神經網路可在 [主要訓練網站](https://katagotraining.org/) 取得。
   * 您可能會想要編輯 `configs/gtp_example.cfg`（請參閱上方的「效能調校」）。
   * 如果使用 OpenCL，您會想要驗證 KataGo 在執行時是否抓取到正確的裝置（例如，某些系統可能同時擁有 Intel CPU OpenCL 和 GPU OpenCL，如果 KataGo 似乎抓錯了，您可以透過在 `configs/gtp_example.cfg` 中指定 `openclGpuToUse` 來修正）。

## Windows
   * 懶人包:
      * 在 Windows 上從原始碼建置實際上這有點棘手，取決於您建置的版本，不一定有超快的方法。
   * 需求
      * 最低版本為 3.18.2 的 CMake，強烈建議使用 GUI 版本 (https://cmake.org/download/)
      * Microsoft Visual Studio for C++。已測試過版本 15 (2017) 應該可以運作，MinGW 版本也應該可以運作，但僅限於 Eigen 和 OpenCL 後端（CUDA 和 TensorRT MinGW 後端 [不受 NVIDIA 支援](https://forums.developer.nvidia.com/t/cuda-with-mingw-how-to-get-cuda-running-under-mingw)）。
      * 如果使用 OpenCL 後端，需要支援 OpenCL 1.2 或更高版本的現代 GPU，或者像[這個](https://software.intel.com/en-us/opencl-sdk)用於 CPU 的東西。但如果使用 CPU，Eigen 應該會更好。
      * 如果使用 CUDA 後端，需要 CUDA 11 或更高版本，以及基於您的 CUDA 版本的相容 CUDNN 版本 (https://developer.nvidia.com/cuda-toolkit) (https://developer.nvidia.com/cudnn) 和支援它們的 GPU。我不確定 CUDA 的版本相容性如何運作，很有可能比這些更高的版本也能運作，但尚未經過測試。
      * 如果使用 TensorRT 後端，除了相容的 CUDA Toolkit (https://developer.nvidia.com/cuda-toolkit) 之外，您還需要至少 8.5 版的 TensorRT (https://developer.nvidia.com/tensorrt)。
      * 如果使用 Eigen 後端，Eigen3, 3.3.x 版。(http://eigen.tuxfamily.org/index.php?title=Main_Page#Download).
      * zlib。在 Windows 上建置 zlib 的簡單方法是使用 vcpkg。在 Powershell 中執行：
         * git clone https://github.com/microsoft/vcpkg.git
         * cd .\vcpkg\
         * .\bootstrap-vcpkg.bat
         * .\vcpkg.exe install zlib:x64-windows
         * 將 CMake ZLIB_LIBRARY 設定為 vcpkg\installed\x64-windows\lib\zlib.lib 並將 ZLIB_INCLUDE_DIRECTORY 設定為 vcpkg\installed\x64-windows\include。
         * 在您建置好 Katago 執行檔後，將 zlib1.dll 從 vcpkg\installed\x64-windows\bin 複製到 Katago 資料夾。
      * libzip (選用，僅用於自我對弈訓練) - 例如 https://github.com/kiyolee/libzip-win-build
      * 對於 MinGW，建議使用 [MSYS2](https://www.msys2.org/) 建置平台來取得必要的 zlib 和 libzip 相依性：
        * 按照官方網站上的說明安裝 MSYS2
        * 從控制台執行 `mingw64.exe` 應用程式
        * 使用 pacman 套件管理員安裝 zlib/libzip 相依性：
          * `pacman -S mingw-w64-x86_64-libzip`
          * `pacman -S mingw-w64-x86_64-xz`
          * `pacman -S mingw-w64-x86_64-bzip2`
          * `pacman -S mingw-w64-x86_64-zstd`
      * 如果編譯以貢獻於公開分散式訓練，需要 OpenSSL (https://www.openssl.org/, https://wiki.openssl.org/index.php/Compilation_and_Installation)。
   * 下載/Clone 此 repo 到某個資料夾 `KataGo`。
   * 使用 CMake GUI 設定並在 IDE 中編譯：
      * 在 [CMake GUI](https://cmake.org/runningcmake/) 中選擇 `KataGo/cpp` 作為原始碼目錄。
      * 將建置目錄設定為您希望產生建置出的執行檔的位置。
      * 點擊 "Configure"。對於產生器選擇您的產生器 (MSVC 或 MinGW)，如果您是 64 位元 Windows，請在選用平台中選擇 "x64"，不要使用 win32。
      * 如果您遇到 CMake 沒有自動找到 ZLib 的錯誤，請根據錯誤訊息將其指向適當的位置：
        * `ZLIB_INCLUDE_DIR` - 將此指向包含 `zlib.h` 和其他標頭檔的目錄
        * `ZLIB_LIBRARY` - 將此指向建置 zlib 產生的 `libz.lib` (`libz.a` for MinGW)。注意 "*_LIBRARY" 期望指向 ".lib" 檔案，而 ".dll" 檔案是執行時需要與 KataGo 一起包含的檔案。
        * 對於 MinGW zlib/libzip CMake 選項應該看起來像這樣：
          ```
          -DZLIB_INCLUDE_DIR="C:/msys64/mingw64/include"
          -DZLIB_LIBRARY="C:/msys64/mingw64/lib/libz.a"
          -DLIBZIP_INCLUDE_DIR_ZIP:PATH="C:/msys64/mingw64/include"
          -DLIBZIP_INCLUDE_DIR_ZIPCONF:PATH="C:/msys64/mingw64/include"
          -DLIBZIP_LIBRARY:FILEPATH="C:/msys64/mingw64/lib/libzip.dll.a"
          ```
      * 還要將 `USE_BACKEND` 設定為 `OPENCL`、`CUDA`、`TENSORRT` 或 `EIGEN`，具體取決於您想要使用的後端。
      * 設定您想要的任何其他選項，並在設定後再次重新執行 "Configure"。例如：
         * 如果您沒有 Git 或 cmake 找不到它，使用 `NO_GIT_REVISION`。
         * 如果您不在乎執行自我對弈訓練且沒有 libzip，使用 `NO_LIBZIP`。
         * 如果您想使用 AVX2 和 FMA 指令編譯，使用 `USE_AVX2`，這將在某些 CPU 上失敗，但在支援它們的 CPU 上會大大加速 Eigen。
         * 使用 `BUILD_DISTRIBUTED` 以支援貢獻資料給公開分散式訓練。
            * 如果建置分散式版本，您也需要建置支援 Git revision，包括在 repo 的 clone 內建置，而不是僅僅是其原始碼的解壓縮副本。
            * 只有特定標籤版本或分支的建置才能貢獻，特別是，不要使用 `master` 分支，請使用最新的 [release](https://github.com/lightvector/KataGo/releases) 標籤或 `stable` 分支的頂端。為了將任何資料不相容或 Bug 的機會降至最低，請不要嘗試使用自訂更改進行貢獻或繞過這些限制。
      * 一旦執行 "Configure" 看起來沒問題，執行 "Generate"，然後在 Visual Studio 或 CLion 中開啟專案並像往常一樣建置。
   * 對於 MinGW，建議透過以下方式設定專案：
     * 在 [CLion IDE](https://www.jetbrains.com/clion/) 中使用預設的 MinGW 工具鏈（非商業用途免費）
     * 使用 [MSYS2](https://www.msys2.org/) MinGW 工具鏈。在設定之前，使用 pacman 套件管理員安裝 gcc 編譯器：`pacman -S mingw-w64-x86_64-gcc`
   * 完成！您現在應該在您的工作目錄中有一個編譯好的 `katago.exe` 執行檔。
   * 注意：您可能需要將與您編譯的各種 ".lib" (".a") 檔案對應的 ".dll" 檔案複製到包含 katago.exe 的目錄中。
     * MinGW 有不同的 dll。如果您使用 pacman，必要的 dll (`libbz2-1.dll`, `libzip.dll`, `libzstd.dll`, `liblzma-5.dll`) 應該從 MinGW bin 目錄（如 `C:\msys64\mingw64\bin`）複製。
   * 注意：如果您不得不更新或安裝 CUDA 或 GPU 驅動程式，您可能需要重新開機才能讓它們運作。
   * 預先訓練的類神經網路可在 [主要訓練網站](https://katagotraining.org/) 取得。
   * 您可能會想要編輯 `configs/gtp_example.cfg`（請參閱上方的「效能調校」）。
   * 如果使用 OpenCL，您會想要驗證 KataGo 是否抓取到正確的裝置（例如，某些系統可能同時擁有 Intel CPU OpenCL 和 GPU OpenCL，如果 KataGo 似乎抓錯了，您可以透過在 `configs/gtp_example.cfg` 中指定 `openclGpuToUse` 來修正）。

## MacOS
   * 懶人包:
     ```
     git clone https://github.com/lightvector/KataGo.git
     cd KataGo/cpp
     # 如果您遇到缺少函式庫的錯誤，請使用您的系統套件管理員安裝適當的套件並重試。
     # -DBUILD_DISTRIBUTED=1 只有在您想回貢獻於公開訓練時才需要。
     cmake -G Ninja -DUSE_BACKEND=METAL -DBUILD_DISTRIBUTED=1
     ninja
     ```
   * 需求
      * [Homebrew](https://brew.sh): `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
      * 最低版本為 3.18.2 的 CMake: `brew install cmake`。
      * AppleClang 和 Swift 編譯器: `xcode-select --install`。
      * 如果使用 Metal 後端，[Ninja](https://ninja-build.org): `brew install ninja`
      * libzip: `brew install libzip`。
      * 如果您想進行自我對弈訓練和研究，可能需要 Google perftools `brew install gperftools` 用於 TCMalloc 或其他更好的 malloc 實作。由於未知原因，在具有大量執行緒和平行對局的自我對弈中的分配模式會導致 glibc malloc 下產生大量記憶體碎片，最終耗盡機器的記憶體，但更好的 mallocs 可以很好地處理這個問題。
      * 如果編譯以貢獻於公開分散式訓練，需要 OpenSSL (`brew install openssl`)。
   * Clone 此 repo:
      * `git clone https://github.com/lightvector/KataGo.git`
   * 在 cpp 目錄中使用 CMake 和 make 編譯：
      * `cd KataGo/cpp`
      * `cmake . -G Ninja -DUSE_BACKEND=METAL` 或 `cmake . -DUSE_BACKEND=OPENCL` 或 `cmake . -DUSE_BACKEND=EIGEN` 取決於您想要哪個後端。
         * 如果使用 TCMalloc，也要指定 `-DUSE_TCMALLOC=1`。
         * 編譯也會呼叫 git 指令將 git hash 嵌入到編譯出的執行檔中，如果這對您造成問題，請指定 `-DNO_GIT_REVISION=1` 來停用它。
         * 指定 `-DUSE_AVX2=1` 以使用 AVX2 和 FMA 支援來編譯 Eigen，這將使其與舊 CPU 不相容，但快得多。Intel 基底並配備新處理器的 Mac 支援 AVX2，但 Apple Silicon Mac 不原生支援 AVX2。（如果您想更進一步，您也可以新增 `-DCMAKE_CXX_FLAGS='-march=native'`，這將專門針對您機器的 CPU 進行最佳化，但執行檔可能根本無法在其他機器上執行）。
         * 指定 `-DBUILD_DISTRIBUTED=1` 以支援貢獻資料給公開分散式訓練。
            * 如果建置分散式版本，您也需要建置支援 Git revision，包括在 repo 的 clone 內建置，而不是僅僅是其原始碼的解壓縮副本。
            * 只有特定標籤版本或分支的建置才能貢獻，特別是，不要使用 `master` 分支，請使用最新的 [release](https://github.com/lightvector/KataGo/releases) 標籤或 `stable` 分支的頂端。為了將任何資料不相容或 Bug 的機會降至最低，請不要嘗試使用自訂更改進行貢獻或繞過這些限制。
      * 對於 Metal 後端使用 `ninja`，或其他後端使用 `make`。
   * 完成！您現在應該在您的工作目錄中有一個編譯好的 `katago` 執行檔。
   * 預先訓練的類神經網路可在 [主要訓練網站](https://katagotraining.org/) 取得。
   * 您可能會想要編輯 `configs/gtp_example.cfg`（請參閱上方的「效能調校」）。
   * 如果使用 OpenCL，您會想要驗證 KataGo 在執行時是否抓取到正確的裝置（例如，某些系統可能同時擁有 Intel CPU OpenCL 和 GPU OpenCL，如果 KataGo 似乎抓錯了，您可以透過在 `configs/gtp_example.cfg` 中指定 `openclGpuToUse` 來修正）。
   * 如果您想在 macOS 上執行 `synchronous_loop.sh`，請執行以下步驟：
      * 安裝 GNU coreutils `brew install coreutils` 以支援可以接受負數的 `head` 工具（在 `train.sh` 中的 `head -n -5`）
      * 安裝 GNU findutils `brew install findutils` 以支援 `find` 工具的 `-printf` 選項，這在 `export_model_for_selfplay.sh` 中被使用。之後，在腳本中將 `find` 修正為 `gfind`。
        注意：您可以嘗試透過使用已安裝的 findutils 調整 `PATH` 來避免修正 `export_model_for_selfplay.sh`：`export PATH="/opt/homebrew/opt/findutils/libexec/gnubin:$PATH"` 或使用別名 `alias find="gfind"`。然而，這並不總是有效。
