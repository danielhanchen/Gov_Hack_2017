library(shiny)
library(ggplot2)

airquality_aggregated <- read.csv("data/aq_aggregated.csv")

# Define server logic required to draw a histogram
shinyServer(function(input, output) {
  airquality_aggregated$date <- as.Date(airquality_aggregated$date)
  
  output$distPlot <- renderPlot({
    
    #plot(airquality_aggregated$date, airquality_aggregated$randwick_aq, type = 'b', xlab = "date", ylab = "airquality")
    ggplot(data=airquality_aggregated, aes(x=date, y=randwick_aq, group=1)) + 
      xlab("Date") + ylab("Local Air Quality") +
      geom_line(colour="blue", size=1.5) + 
      geom_point(colour="blue", size=4, shape=21, fill="white")
  })
  
})



