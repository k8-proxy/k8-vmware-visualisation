# jupyter-notebooks:

- [Architectural Diagram](#architectural-diagram)
- [VMs-visualisations-0](#VMs-visualisations-0)
- [VMs-visualisations-1](#VMs-visualisations-1)
- [VMs-visualisations-2](#VMs-visualisations-2)
- [K8-vmware Project Tracking](#project-tracking)
- [Release Visualisation](#release-visualisation)
- [Release Presentation](#release-presentation)
- [Screenshots](#screenshots)


<a id="architectural-diagram"></a>
## Architectural Diagram

This notebook shows the general work-flow to extract the data that will be visualise in the other notebooks.


The data needed for the next three notebooks is pulled from

https://wmwaredata.s3.us-east-2.amazonaws.com/machines.json

<a id="VMs-visualisations-0"></a>
## VMs-visualisations-0

Initian barcharts and piecharts visualisations.


<a id="VMs-visualisations-1"></a>
## VMs-visualisations-1

VM Ware EXSi network visualisation using Visjs. Hierarchy and No Hierarchy versions.


<a id="VMs-visualisations-2"></a>
## VMs-visualisations-2

More VM Ware EXSi Visjs network visualisations. In this case we visualise each VM as a subnetwork connected to a Host node.


<a id="project-tracking"></a>
## K8-vmware Project Tracking

This notebook pulls data about K8-vmware Project Tracking from this google sheet

https://docs.google.com/spreadsheets/d/13L9OodSo4Gp1vKPKpqEsi8vuoaxefuqhR6adXEvux5o/edit#gid=0

To autocreate a google slide presentation that is saved to this folder:

https://drive.google.com/drive/u/1/folders/1dELfGV6IMMII97tTjqSXeJwPAMEjtbDX

See more related info here:

https://docs.google.com/spreadsheets/d/1SetbtWlZC9fEddTbOzlnM36OQYBdtg0bbG4quq9ODKY/edit#gid=1064322020


<a id="release-visualisation"></a>
## Release Visualisation

Repo's releases visualisations.

The data needed for this notebook is get from here

https://wmwaredata.s3.us-east-2.amazonaws.com/releases.json


<a id="release-presentation"></a>
## Release Presentation

This notebook create a google slide presentation about Releases that is saved to this folder:

https://drive.google.com/drive/u/1/folders/1dELfGV6IMMII97tTjqSXeJwPAMEjtbDX


# HTML pages

All the networks visualized inside the notebooks can also be visualized in the html pages that you can find in the 'html pages' folder.

To be able to visualize the html pages you will need to run a local server.

If you are using **Ubuntu**, to start the http server on an specific port, for instance port 8080, simply type:

```
    python -m http.server 8080
```

## How to take screen shoots of the html pages locally

<a id="screenshots"></a>
## Screenshots

Run this notebook to take screenshots of the html pages. It uses selenium package, therefore you need to have Chrome installed in the default location for each system:

- Mac users with Homebrew installed: brew tap homebrew/cask && brew cask install chromedriver
- Debian based Linux distros: sudo apt-get install chromium-chromedriver
- Windows users with Chocolatey installed: choco install chromedriver

You also must have the html pages running on a local server for it to work. 

Taken screenshots are saved to data folder.

