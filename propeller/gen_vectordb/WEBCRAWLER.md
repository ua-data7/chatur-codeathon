# Web Crawler
Crawl web content

Katana: [https://blog.projectdiscovery.io/introducing-katana-the-best-cli-web-crawler/](https://blog.projectdiscovery.io/introducing-katana-the-best-cli-web-crawler/)


## Install Katana
```
go install github.com/projectdiscovery/katana/cmd/katana@latest
```

## Run
```
katana -u https://techlaunch.arizona.edu -d 3 -kf sitemap.xml -o link.url
```