#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import shutil
import subprocess
import urllib.request
from pathlib import Path

from common import PIPELINE_VERSION, build_representative_introns, write_tsv

ENSEMBL_RELEASE = "113"
FASTA_URL = "https://ftp.ensembl.org/pub/release-113/fasta/caenorhabditis_elegans/dna/Caenorhabditis_elegans.WBcel235.dna.toplevel.fa.gz"
GTF_URL = "https://ftp.ensembl.org/pub/release-113/gtf/caenorhabditis_elegans/Caenorhabditis_elegans.WBcel235.113.gtf.gz"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    tmp = path.with_suffix(path.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": f"JM105-Celegans/{PIPELINE_VERSION}"})
    with urllib.request.urlopen(request, timeout=300) as response, tmp.open("wb") as out:
        shutil.copyfileobj(response, out)
    tmp.replace(path)


def gunzip_file(source: Path, target: Path) -> None:
    if target.exists() and target.stat().st_size > 0:
        return
    tmp = target.with_suffix(target.suffix + ".part")
    with gzip.open(source, "rb") as inp, tmp.open("wb") as out:
        shutil.copyfileobj(inp, out)
    tmp.replace(target)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--star", required=True, type=Path)
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()

    root = args.root.resolve()
    ref = root / "work" / "reference" / "WBcel235_Ensembl113"
    ref.mkdir(parents=True, exist_ok=True)
    fasta_gz = ref / "Caenorhabditis_elegans.WBcel235.dna.toplevel.fa.gz"
    gtf_gz = ref / "Caenorhabditis_elegans.WBcel235.113.gtf.gz"
    fasta = ref / "Caenorhabditis_elegans.WBcel235.dna.toplevel.fa"
    gtf = ref / "Caenorhabditis_elegans.WBcel235.113.gtf"
    star_index = ref / "STAR_index"

    download(FASTA_URL, fasta_gz)
    download(GTF_URL, gtf_gz)
    gunzip_file(fasta_gz, fasta)
    gunzip_file(gtf_gz, gtf)

    introns = build_representative_introns(gtf)
    intron_rows = [
        {
            "intron_id": x.intron_id,
            "gene_id": x.gene_id,
            "gene_name": x.gene_name,
            "transcript_id": x.transcript_id,
            "chrom": x.chrom,
            "start0": x.start0,
            "end0": x.end0,
            "strand": x.strand,
            "intron_length": x.intron_length,
        }
        for x in introns
    ]
    write_tsv(
        ref / "representative_protein_coding_introns.tsv.gz",
        intron_rows,
        ["intron_id", "gene_id", "gene_name", "transcript_id", "chrom", "start0", "end0", "strand", "intron_length"],
    )

    complete = star_index / "Genome"
    if not complete.exists():
        star_index.mkdir(parents=True, exist_ok=True)
        command = [
            str(args.star),
            "--runMode", "genomeGenerate",
            "--runThreadN", str(args.threads),
            "--genomeDir", str(star_index),
            "--genomeFastaFiles", str(fasta),
            "--sjdbGTFfile", str(gtf),
            "--sjdbOverhang", "149",
        ]
        subprocess.run(command, check=True)

    manifest = [
        "key\tvalue",
        f"pipeline_version\t{PIPELINE_VERSION}",
        f"ensembl_release\t{ENSEMBL_RELEASE}",
        "assembly\tWBcel235",
        f"fasta_url\t{FASTA_URL}",
        f"gtf_url\t{GTF_URL}",
        f"fasta_sha256\t{sha256(fasta)}",
        f"gtf_sha256\t{sha256(gtf)}",
        f"intron_count\t{len(introns)}",
        f"star_index\t{star_index}",
    ]
    (ref / "REFERENCE_MANIFEST.tsv").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    (ref / "REFERENCE_COMPLETE.txt").write_text("SUCCESS\n", encoding="utf-8")
    print(f"Reference ready: {ref}")


if __name__ == "__main__":
    main()
