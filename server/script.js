window.onload = () => {
    let $ = document.querySelector.bind(document);

    $("#clock").addEventListener("click", () => {
        fetch("http://192.168.40.131/clock", {
            mode: "no-cors"
        })
    })

    $("#timer").addEventListener("click", () => {
        let secs = Number($("#timer_m").value) * 60 + Number($("#timer_s").value);
        console.log(secs)
        fetch(`http://192.168.40.131/timer?t=${secs}`, {
            mode: "no-cors"
        })
    })

    $("#pause-timer").addEventListener("click", () => {
        fetch("http://192.168.40.131/timer/pause", {
            mode: "no-cors"
        })
    })

    $("#unpause-timer").addEventListener("click", () => {
        fetch("http://192.168.40.131/timer/unpause", {
            mode: "no-cors"
        })
    })

    $("#stopwatch").addEventListener("click", () => {
        fetch("http://192.168.40.131/stopwatch", {
            mode: "no-cors"
        })
    })

    $("#pause-stopwatch").addEventListener("click", () => {
        fetch("http://192.168.40.131/stopwatch/pause", {
            mode: "no-cors"
        })
    })

    $("#unpause-stopwatch").addEventListener("click", () => {
        fetch("http://192.168.40.131/stopwatch/unpause", {
            mode: "no-cors"
        })
    })

    $("#arcade").addEventListener("click", () => {
        fetch("http://192.168.40.131/arcade", {
            mode: "no-cors"
        })
    })
}