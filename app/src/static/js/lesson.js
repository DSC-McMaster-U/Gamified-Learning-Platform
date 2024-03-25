// HTML DOM Elements
const tabDropdown = document.querySelectorAll(".tabs-dropdown > button");
const tabLessons = document.querySelectorAll(".tabs-activity.tab-lesson a");
const tabQuizzes = document.querySelectorAll(".tab-activity.tab-quiz a");
const panelContainer = document.querySelector("#lesson-panels");
const links = document.querySelectorAll("a.textbook-download");
const videoElements = document.querySelectorAll(".lesson-video");
const videoPlayers = {}; // ...in case if these videos ever have to be accessed in the future

/**
 * This function is called whenever a lesson tab is clicked, causing
 * the current panel to be halted & erased with the tab's respective panel to be rendered on the right
 * of the screen.
**/
function togglePanel() {
    let panelBtn = this.querySelector("button");

    let panelRef = this.hash;
    let panel = panelContainer.querySelector(":scope > " + panelRef);
    let otherPanels = panelContainer.querySelectorAll(`:scope > :not([id="${panelRef.slice(1)}"])`);

    // Debug for filtering proper panels
    // console.log(panel);
    // console.log(otherPanels);

    if (panel != null) {
        otherPanels.forEach((otherPanel) => {
            otherPanel.classList.remove("show-panel");

            if (otherPanel.getAttribute("panel-type") == "video") {
                let video = otherPanel.querySelector("video");

                videoPlayers[video.id].stop();
            }
        });

        tabLessons.forEach((otherTab) => {
            otherTab.querySelector("button").classList.remove("menu-open");
        })

        panel.classList.add("show-panel");
        panelBtn.classList.add("menu-open");
    }
}

/**
 * This function is called whenever a parent tab with dropdown contents is clicked, causing
 * the element and its parent tab menus (if any) to toggle active classes ("menu-open") and 
 * increase/decrease in height size accordingly.
**/
function toggleDropdown() {
    let subMenu = this.nextElementSibling;
    let subMenuItems = subMenu.querySelectorAll(":scope>li");
    let parentMenu = this.closest("ul");
    let numSubMenuHeight = 0;

    this.classList.toggle("menu-open");

    if (this.classList.contains("menu-open")) {
        subMenuItems.forEach((item) => {
            numSubMenuHeight += item.offsetHeight;
        })

        subMenu.style.maxHeight = `${numSubMenuHeight}px`;

        if (parentMenu != null) {
            let parentMenuHeight = parentMenu.style.maxHeight;
            parentMenuHeight = parentMenuHeight.slice(0, -2);

            parentMenu.style.maxHeight = `${parseInt(parentMenuHeight) + numSubMenuHeight}px`
        }
    } else {
        subMenu.style.maxHeight = "0px";
    }
}

/**
 * When the lessons page's HTML is first loaded, this function is called to setup certain
 * page elements before the visual elements are rendered for the user. These elements include
 * certain link text displays (depending on the screen width of the device), video players for 
 * lessons with their associated videos, and the automatic opening of one of the lessons and its tabs.
 * 
 * Regarding the lessons + tabs: if the website link contains no hash value pointing to a specific panel ID, 
 * then the first lesson in the course is open by default; otherwise, the lesson referenced in the link by 
 * ID is open, alongside its corresponding tabs in the vertical tab structure to the left of the page).
 */
function pageSetup() {
    let currentLink = window.location.href;
    let currentPanelID = currentLink.split("#")[1];
    let tab, parentTab, parentParentTab;

    // Setup textbook download link displays
    if (window.innerWidth < 570) {
        links.forEach((link) => {
            link.textContent = "Download textbook here...";
        });
    } else {
        links.forEach((link) => {
            link.textContent = "DOWNLOAD";
        });
    }

    // Plyr.js Elements - Add in proper video sources + thumbnails, and initialize Plyr objects using video element IDs
    for (let videoElement of videoElements) {
        let video = videoElement.querySelector("video");
        let source = videoElement.querySelector("source");
        let videoPathID = video.id.slice(6);
        let videoFilename = video.getAttribute('data-video-filename')
        let thumbnailFilename = video.getAttribute('data-thumbnail-filename')
        let videoPath = `../static/vendor/lesson-videos/${videoPathID}/`;
        let videoPlayer;

        source.src = videoPath + videoFilename;
        video.setAttribute("data-poster", videoPath + thumbnailFilename);
        video.load();

        videoPlayer = new Plyr(`#${video.id}`);
        videoPlayers[video.id] = videoPlayer;
    }

    // Depending on if url contains hashtagged element, automatically open the respective lesson and its tabs
    if (currentPanelID == null) {
        tab = tabLessons[0];
    } else {
        tab = document.querySelector(`a[href="#${currentPanelID}"]`);
    }

    parentTab = tab.closest("ul").previousElementSibling;
    parentParentTab = parentTab.closest("ul").previousElementSibling;

    toggleDropdown.call(parentParentTab, null)
    toggleDropdown.call(parentTab, null)
    togglePanel.call(tab, null)
}

function main() {
    document.addEventListener("DOMContentLoaded", pageSetup);

    window.addEventListener("resize", () => {            
        if (window.innerWidth <= 600) {
            links.forEach((link) => {
                link.textContent = "Download textbook here...";
            });
        } else {
            links.forEach((link) => {
                link.textContent = "DOWNLOAD";
            });
        }
    });

    tabDropdown.forEach((tab) => {
        tab.addEventListener("click", toggleDropdown);
    });

    tabLessons.forEach((tab) => {
        tab.addEventListener("click", togglePanel);
    });
}

main();
