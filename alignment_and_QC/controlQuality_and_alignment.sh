#!/usr/bin/env bash

for i in $(tr -d '\r' < sra1.txt)
do
    output_dir="/create/path/to/results/${i}"
    mkdir -p "$output_dir"
    cd "$output_dir" || { echo "Erro ao entrar no diretório $output_dir"; exit 1; }

    #rm "${i}.log.txt"

    # Define o arquivo de log
    log_file="${output_dir}/${i}.log.txt"

    # Início do log
    echo "[$(date)] Início do processamento da amostra ${i}" | tee -a "$log_file"

    {
        #rm -r "${i}_1.fastq.gz"
        #rm -r "${i}_2.fastq.gz"

        #ln -s /path/to/genome/reference/Homo_sapiens_assembly38.fasta

        #echo "[$(date)] Linkando e indexando a referência..."
        #bwa index Homo_sapiens_assembly38.fasta

        echo "[$(date)] Alinhando com bwa mem..."
        bwa mem -t 20 -M -R "@RG\tID:${i}\tSM:${i}\tPL:ILLUMINA" \
        Homo_sapiens_assembly38.fasta \
        "${i}_R1_paired.fastq.gz" "${i}_R2_paired.fastq.gz" | \
        samtools view -bS -h -F 4 - > output.map.bam

        echo "[$(date)] Ordenando e processando com Picard..."
        ln -s /path/to/software/picard.jar
        ln -s /path/to/Homo_sapiens_assembly38.dict
        mkdir -p TMP

        java -XX:ParallelGCThreads=40 -Xmx10G -jar picard.jar SortSam \
        I=output.map.bam O=output.sorted.bam SORT_ORDER=coordinate \
        VALIDATION_STRINGENCY=LENIENT TMP_DIR=./TMP

        java -XX:ParallelGCThreads=40 -Xmx10G -jar picard.jar ReorderSam \
        I=output.sorted.bam O=output.reorder.bam \
        R=Homo_sapiens_assembly38.fasta \
        ALLOW_CONTIG_LENGTH_DISCORDANCE=TRUE \
        VALIDATION_STRINGENCY=LENIENT TMP_DIR=./TMP

        java -XX:ParallelGCThreads=40 -Xmx10G -jar picard.jar MarkDuplicates \
        I=output.reorder.bam O=output.dup.bam \
        METRICS_FILE=output.reorder.bam.mtrcs \
        REMOVE_DUPLICATES=true CREATE_INDEX=true TMP_DIR=./TMP

        echo "[$(date)] Linkando arquivos do GATK..."
        samtools faidx Homo_sapiens_assembly38.fasta

        echo "[$(date)] Rodando GATK BaseRecalibrator..."
        java -Djava.io.tmpdir=./TMP -Xmx4G -jar ../../software/gatk-package-4.1.9.0-local.jar BaseRecalibrator \
        --intervals /path/to/bed/file/DHS-5000Z.primers-150bp.bed \
        --interval-padding 100 \
        -R ../../genome_reference/Homo_sapiens_assembly38.fasta \
        -I output.dup.bam \
        -O output.rec.bam \
        --known-sites ../../database/dbSNP151.hg38.vcf.gz \
        --known-sites ../../database/1000G_omni2.5.hg38.vcf.gz \
        --known-sites ../../database/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz

        java -Djava.io.tmpdir=./TMP -Xmx4G -jar gatk-package-4.1.9.0-local.jar ApplyBQSR -R Homo_sapiens_assembly38.fasta -L /path/to/bed/file/DHS-5000Z.primers-150bp.bed --interval-padding 100 -I output.dup.bam -O output.bqsr.bam --bqsr-recal-file output.rec.bam

        echo "[$(date)] Finalizado com sucesso a amostra ${i}"
        echo "--------------------------------------- \n"

    } >> "$log_file" 2>&1

    echo "[$(date)] Log finalizado: ${log_file}"
    echo "---------------------------------------"

done
