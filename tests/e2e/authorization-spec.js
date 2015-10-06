describe('Get a user to login and show dashboard:', function() {
    it('should let a user login', function() {
        driver = browser.driver;

        driver.get('http://172.17.42.1:8083/login/');

        expect(driver.getTitle()).toEqual('HelloLily | Login');

        driver.findElement(By.id('id_username')).sendKeys('user1@lily.com');
        driver.findElement(By.id('id_password')).sendKeys('testing');
        driver.findElement(By.id('id_password')).submit();

        expect(driver.getTitle()).toEqual('HelloLily | Welcome!');
    });
});
