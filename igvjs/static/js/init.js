function initBrowser() {
  var div,
          options,
          browser;

  div = $("#myDiv")[0];
  options = {
      reference: {
          id: "hg19",
          fastaURL: "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/1kg_v37/human_g1k_v37_decoy.fasta",
          cytobandURL: "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/b37/b37_cytoband.txt"
      },
      locus: "22:24,375,771-24,376,878",
      tracks:
              [
                  {
                      name: "Genes",
                      searchable: false,
                      type: "annotation",
                      format: "gtf",
                      sourceType: "file",
                      url: "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg19/genes/gencode.v18.annotation.sorted.gtf.gz",
                      indexURL: "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg19/genes/gencode.v18.annotation.sorted.gtf.gz.tbi",
                      visibilityWindow: 10000000,
                      order: Number.MAX_VALUE,
                      displayMode: "EXPANDED"
                  },
                  {
                      url: 'static/data/public/gstt1_sample.bam',
                      name: 'GSTT1 Alignments',
                      height: 500
                  }
              ]
  };

  browser = igv.createBrowser(div, options);
}
