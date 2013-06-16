
graph = function (means, qtext, ttext, loc) {

    var barStart = 40;
    var barWidth = 30;
    var barSpace = 25;
    var widthPad = 40; /* was 20, had commented go back to 40, now at 40... was I right before or now? */
    var heightPad = 80;
    var yOffset = 20;
    var xOffset = widthPad/2;
    var height = (barWidth + barSpace) * means.length + heightPad;
    var width = 600 + widthPad;

    var xScale = d3.scale.linear()
        .domain([0, 5])
        .range([widthPad/2, width - widthPad]);

    var yScale = d3.scale.linear()
        .domain([0, means.length])
        .range([barStart, height]);

    var sampleSVG = d3.select(loc)
        .append("xhtml:div")
        .attr("style", "box-shadow: 0 0 8px #000000; -webkit-box-shadow: 0 0 8px #000000; -moz-box-shadow: 0 0 8px #000000; height:" + height + "px; width:" + width + "px;")
        .append("svg")
        .attr("height", height)
        .attr("width", width);


    sampleSVG.append("rect")
        .attr("fill", "snow")
        .attr("stroke", "orange")
        .attr("stroke-width", 8)
        .attr("opacity", .80)
        .attr("height", height)
        .attr("width", width);

    sampleSVG.selectAll("rect.behindbar")
        .data(means)
	.enter().append("rect")
        .attr("x", xOffset)
        .attr("y", function(d, i){return yScale(i) + yOffset;})
        .attr("width", 0)
        .attr("height", barWidth)
        .attr("fill-opacity", 0)
        .attr("class", "behindbar")
        .transition().delay(100).duration(1300)
	.attr("fill-opacity", 1)
        .attr("width", xScale(5));

    sampleSVG.selectAll("rect.graphbar")
        .data(means)
        .enter().append("rect")
        .attr("x", xOffset)
        .attr("y", function(d, i){return yScale(i) + yOffset;})
        .attr("height", barWidth)
        .attr("class", "graphbar")
        .attr("width", 0)
	.transition().delay(300).duration(1300)
        .attr("width", function(d, i){return xScale(d)});

    sampleSVG.selectAll("rect.graphbar")                                                       
        .data(ttext);

    sampleSVG.selectAll("text.bartext")
        .data(means)
        .enter().append("text")
        .attr("x", function(d, i){ if (parseFloat(d) > 2) {return xScale(d)} else {return xScale(d) + xOffset  + 10}})
        .attr("dx", -xOffset)
        .attr("y", function(d, i){return yScale(i) + yOffset;})
        .attr("dy", barWidth/2 + 5)
        .text(function(d) { return d;})
        .attr("class", "bartext")
	.attr("fill-opacity", 0)
	.transition().delay(1000).duration(1300)
	.attr("fill-opacity", 1);

    sampleSVG.selectAll("text.q")
        .data(qtext)
        .enter().append("text")
        .attr("class", "q")
        .attr("x", xOffset)
        .attr("y", function(d, i){return yScale(i)})
        .attr("dy", 13)
        .attr("style", "font-size: 100%")
        .attr("fill", "black")
        .text(function(d) {return d;})
	.attr("fill-opacity", 0)
	.transition().delay(500).duration(1300)
	.attr("fill-opacity", 1);
    
    var tb = sampleSVG
        .append("text")
        .text("Course Evaluations: ")
        .attr("class", "taughtby")
        .attr("x", xOffset)
        .attr("y", barStart - 15);
    
    var toptext = [5]

    sampleSVG.selectAll("text.five").data(toptext)
        .enter().append("text")
        .text(function(d){return d;})
	.attr("class", "five")
	.attr("class", "bartext")
        .attr("x", function(d){return xScale(d) + 6;})
        .attr("y", yScale(0) - 5)
        .attr("dy", 13)
	.attr("fill-opacity", 0)
        .transition().delay(1000).duration(1300)
        .attr("fill-opacity", 1);

}