function initBrowser() {

  var div,
          options,
          browser;

  div = document.getElementById("myDiv");
  options = {
      genome: "hg19",
      //locus: "22:24,375,771-24,376,878",
      tracks: [
                  {
                      url: 'static/data/public/test.bw',
                      name: 'BigWig'
                  },
                  {
                      url: 'static/data/public/test.bedGraph',
                      name: 'bedgraph'
                  }
              ]
  };

  browser = igv.createBrowser(div, options);
}
