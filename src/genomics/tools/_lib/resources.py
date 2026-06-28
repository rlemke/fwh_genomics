"""Static resource registry + alias maps for the genomics example.

Both the cache handlers (which yield factory-built handlers for each
registry entry) and the resolve handlers (which do alias / accession
lookup over the same registry) read from these tables. Keeping them
here means the registry is the single source of truth for what's
"cached" in this example.
"""

from __future__ import annotations

import os

# Configurable cache base directory (supports hdfs:// URIs)
CACHE_BASE = os.environ.get("FW_GENOMICS_CACHE_DIR", "/cache")


# Registry: namespace -> {facet_name -> (url, path, size_bytes, resource_type)}
RESOURCE_REGISTRY: dict[str, dict[str, tuple[str, str, int, str]]] = {
    "genomics.cache.reference": {
        "GRCh38": (
            "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/GRCh38_major_release_seqs_for_alignment_pipelines/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gz",
            f"{CACHE_BASE}/reference/GRCh38/GRCh38.fa.gz",
            3_200_000_000,
            "reference",
        ),
        "GRCh37": (
            "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.14_GRCh37.p13/GRCh37_major_release_seqs_for_alignment_pipelines/GCA_000001405.14_GRCh37_no_alt_analysis_set.fna.gz",
            f"{CACHE_BASE}/reference/GRCh37/GRCh37.fa.gz",
            3_100_000_000,
            "reference",
        ),
        "T2TCHM13": (
            "https://s3-us-west-2.amazonaws.com/human-pangenomics/T2T/CHM13/assemblies/analysis_set/chm13v2.0.fa.gz",
            f"{CACHE_BASE}/reference/T2TCHM13/chm13v2.0.fa.gz",
            3_050_000_000,
            "reference",
        ),
        "Hg19": (
            "https://hgdownload.cse.ucsc.edu/goldenpath/hg19/bigZips/hg19.fa.gz",
            f"{CACHE_BASE}/reference/hg19/hg19.fa.gz",
            3_000_000_000,
            "reference",
        ),
        "GRCm39": (
            "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/635/GCA_000001635.9_GRCm39/GRCm39_major_release_seqs_for_alignment_pipelines/GCA_000001635.9_GRCm39_no_alt_analysis_set.fna.gz",
            f"{CACHE_BASE}/reference/GRCm39/GRCm39.fa.gz",
            2_700_000_000,
            "reference",
        ),
    },
    "genomics.cache.annotation": {
        "DbSNP156": (
            "https://ftp.ncbi.nih.gov/snp/latest_release/VCF/GCF_000001405.40.gz",
            f"{CACHE_BASE}/annotation/dbsnp156/dbsnp156.vcf.gz",
            15_000_000_000,
            "annotation",
        ),
        "DbSNP155": (
            "https://ftp.ncbi.nih.gov/snp/archive/b155/VCF/GCF_000001405.39.gz",
            f"{CACHE_BASE}/annotation/dbsnp155/dbsnp155.vcf.gz",
            14_500_000_000,
            "annotation",
        ),
        "ClinVar": (
            "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz",
            f"{CACHE_BASE}/annotation/clinvar/clinvar.vcf.gz",
            300_000_000,
            "annotation",
        ),
        "GnomAD4": (
            "https://storage.googleapis.com/gcp-public-data--gnomad/release/4.0/vcf/genomes/gnomad.genomes.v4.0.sites.vcf.bgz",
            f"{CACHE_BASE}/annotation/gnomad4/gnomad4.vcf.gz",
            450_000_000_000,
            "annotation",
        ),
        "GnomAD3": (
            "https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.vcf.bgz",
            f"{CACHE_BASE}/annotation/gnomad3/gnomad3.vcf.gz",
            350_000_000_000,
            "annotation",
        ),
        "VepCache112": (
            "https://ftp.ensembl.org/pub/release-112/variation/vep/homo_sapiens_vep_112_GRCh38.tar.gz",
            f"{CACHE_BASE}/annotation/vep112/homo_sapiens_vep_112_GRCh38.tar.gz",
            20_000_000_000,
            "annotation",
        ),
        "Gencode46": (
            "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_46/gencode.v46.annotation.gtf.gz",
            f"{CACHE_BASE}/annotation/gencode46/gencode.v46.annotation.gtf.gz",
            50_000_000,
            "annotation",
        ),
    },
    "genomics.cache.sra": {
        "SRR622461": (
            "https://sra-pub-run-odp.s3.amazonaws.com/sra/SRR622461/SRR622461",
            f"{CACHE_BASE}/sra/SRR622461/SRR622461.sra",
            25_000_000_000,
            "sra",
        ),
        "SRR622458": (
            "https://sra-pub-run-odp.s3.amazonaws.com/sra/SRR622458/SRR622458",
            f"{CACHE_BASE}/sra/SRR622458/SRR622458.sra",
            22_000_000_000,
            "sra",
        ),
        "SRR622459": (
            "https://sra-pub-run-odp.s3.amazonaws.com/sra/SRR622459/SRR622459",
            f"{CACHE_BASE}/sra/SRR622459/SRR622459.sra",
            23_000_000_000,
            "sra",
        ),
        "ERR009378": (
            "https://sra-pub-run-odp.s3.amazonaws.com/sra/ERR009378/ERR009378",
            f"{CACHE_BASE}/sra/ERR009378/ERR009378.sra",
            18_000_000_000,
            "sra",
        ),
        "SRR13604789": (
            "https://sra-pub-run-odp.s3.amazonaws.com/sra/SRR13604789/SRR13604789",
            f"{CACHE_BASE}/sra/SRR13604789/SRR13604789.sra",
            30_000_000_000,
            "sra",
        ),
    },
}


# Per-reference contig metadata used to size aligner indexes.
REFERENCE_CONTIGS: dict[str, tuple[int, int]] = {
    "GRCh38": (195, 3_088_286_401),
    "GRCh37": (84, 3_101_804_739),
    "T2TCHM13": (24, 3_117_292_070),
    "Hg19": (93, 3_137_161_264),
    "GRCm39": (61, 2_728_222_451),
}

ALIGNER_VERSIONS: dict[str, str] = {
    "bwa": "bwa-mem2-2.2.1",
    "star": "STAR-2.7.11b",
    "bowtie2": "bowtie2-2.5.3",
}

ALIGNER_SIZE_MULTIPLIERS: dict[str, float] = {
    "bwa": 1.5,
    "star": 10.0,
    "bowtie2": 1.2,
}

# Index registry: namespace -> [reference names]
INDEX_REGISTRY: dict[str, list[str]] = {
    "genomics.cache.index.bwa": ["GRCh38", "GRCh37", "T2TCHM13", "Hg19", "GRCm39"],
    "genomics.cache.index.star": ["GRCh38", "GRCh37", "T2TCHM13"],
    "genomics.cache.index.bowtie2": ["GRCh38", "GRCh37"],
}


# Alias maps for the Resolve namespace.
REFERENCE_ALIASES: dict[str, tuple[str, str]] = {
    "hg38": ("genomics.cache.reference", "GRCh38"),
    "grch38": ("genomics.cache.reference", "GRCh38"),
    "hg37": ("genomics.cache.reference", "GRCh37"),
    "grch37": ("genomics.cache.reference", "GRCh37"),
    "t2t": ("genomics.cache.reference", "T2TCHM13"),
    "t2t-chm13": ("genomics.cache.reference", "T2TCHM13"),
    "chm13": ("genomics.cache.reference", "T2TCHM13"),
    "t2tchm13": ("genomics.cache.reference", "T2TCHM13"),
    "hg19": ("genomics.cache.reference", "Hg19"),
    "grcm39": ("genomics.cache.reference", "GRCm39"),
    "mm39": ("genomics.cache.reference", "GRCm39"),
}

ANNOTATION_ALIASES: dict[str, tuple[str, str]] = {
    "dbsnp": ("genomics.cache.annotation", "DbSNP156"),
    "dbsnp156": ("genomics.cache.annotation", "DbSNP156"),
    "dbsnp155": ("genomics.cache.annotation", "DbSNP155"),
    "clinvar": ("genomics.cache.annotation", "ClinVar"),
    "gnomad": ("genomics.cache.annotation", "GnomAD4"),
    "gnomad4": ("genomics.cache.annotation", "GnomAD4"),
    "gnomad3": ("genomics.cache.annotation", "GnomAD3"),
    "vep": ("genomics.cache.annotation", "VepCache112"),
    "vep112": ("genomics.cache.annotation", "VepCache112"),
    "gencode": ("genomics.cache.annotation", "Gencode46"),
    "gencode46": ("genomics.cache.annotation", "Gencode46"),
}
