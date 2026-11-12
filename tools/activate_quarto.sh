# Source this: puts the Quarto build for this machine's architecture on PATH.
case "$(uname -m)" in
    x86_64)  export PATH=/work/nvme/bbjs/sjin2/tools/quarto-1.10.19-amd64/bin:$PATH ;;
    aarch64) export PATH=/work/nvme/bbjs/sjin2/tools/quarto-1.10.19-arm64/bin:$PATH ;;
esac
