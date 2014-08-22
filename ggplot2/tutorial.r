# http://www.noamross.net/blog/2012/10/5/ggplot-introduction.html 

library('ggplot2')

plot1 = function() {
     a <- ggplot(data = msleep, aes(x = bodywt, y = sleep_total))
     a <- a + geom_point()
     a <- a + xlab("Body Weight") + ylab("Total Hours Sleep") + ggtitle("Some Sleep Data")
     a
}

mysave = function(plt) {
    ggsave("sleepplot.png", plot = plt, width = 4, height = 4)
}

plot2 = function() {
     a <- ggplot(data = msleep, aes(x = bodywt, y = sleep_total, col = vore))
     a <- a + geom_point()
     a <- a + xlab("Body Weight") + ylab("Total Hours Sleep") + ggtitle("Some Sleep Data")
     a
}

plot3 = function() {
     a <- ggplot(data = msleep, aes(x = log(bodywt), y = sleep_rem/sleep_total, col = vore))
     a <- a + geom_point(size = 5)
     a <- a + xlab("Log Body Weight") + ylab("Fraction of sleep that is REM") + ggtitle("Some Sleep Data") + scale_color_discrete(name = "Tropic Level")
     a
}

plot_facet = function() {
     a <- ggplot(data = msleep, aes(x = log(bodywt), y = sleep_rem/sleep_total))
     a <- a + geom_point(size = 5)
     a <- a + facet_wrap(~vore)
     a <- a + xlab("Log Body Weight") + ylab("Fraction of sleep that is REM") + ggtitle("Some Sleep Data") + scale_color_discrete(name = "Tropic Level")
     a
}

plot_facet2 = function() {
     a <- ggplot(data = msleep, aes(x = log(bodywt), y = sleep_rem/sleep_total))
     a <- a + geom_point(size = 2)
     a <- a + facet_grid(conservation ~ vore)
     a <- a + xlab("Log Body Weight") + ylab("Fraction of sleep that is REM") + ggtitle("Some Sleep Data") + scale_color_discrete(name = "Tropic Level")
     a
}

plot_l1 = function() {
    p = ggplot(economics, aes(x = date, y = unemploy)) + geom_line() 
    p
}

plot_l2 = function() {
    p = ggplot(economics, aes(x = date, y = unemploy)) + geom_line() 
    p = p + geom_smooth()
    p
}
