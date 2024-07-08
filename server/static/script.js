window.onload = () => {
    let $ = document.querySelector.bind(document);

    $("#clock").addEventListener("click", () => {
        fetch("/proxy/clock", {
            mode: "no-cors"
        })
    })

    $("#timer").addEventListener("click", () => {
        let secs = Number($("#timer_m").value) * 60 + Number($("#timer_s").value);
        console.log(secs)
        fetch(`/proxy/timer/t=${secs}`, {
            mode: "no-cors"
        })
    })

    $("#pause-timer").addEventListener("click", () => {
        fetch("/proxy/timer/pause", {
            mode: "no-cors"
        })
    })

    $("#unpause-timer").addEventListener("click", () => {
        fetch("/proxy/timer/unpause", {
            mode: "no-cors"
        })
    })

    $("#stopwatch").addEventListener("click", () => {
        fetch("/proxy/stopwatch", {
            mode: "no-cors"
        })
    })

    $("#pause-stopwatch").addEventListener("click", () => {
        fetch("/proxy/stopwatch/pause", {
            mode: "no-cors"
        })
    })

    $("#unpause-stopwatch").addEventListener("click", () => {
        fetch("/proxy/stopwatch/unpause", {
            mode: "no-cors"
        })
    })

    $("#arcade").addEventListener("click", () => {
        fetch("/proxy/arcade", {
            mode: "no-cors"
        })
    })
}