using OpenQA.Selenium;
using OpenQA.Selenium.Firefox;

namespace e2e_tests;

public class UnitTest1
{
    [Fact]
    public void ApplicationLoads()
    {
        using var driver = new FirefoxDriver();

        driver.Navigate().GoToUrl("http://localhost:4200");

        var heading = driver.FindElement(By.TagName("h1"));

        Assert.Equal("PSR-Lens", heading.Text);
    }
}
