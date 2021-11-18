export default {
  waitForElement: (id, container=document) => {
    return new Promise((resolve, reject) => {
      const checkExist = setInterval(function() {
        const elem = container.getElementById(id);
        if (elem) {
          resolve(elem)
          clearInterval(checkExist);
          return;
        }
     }, 500);
    });
  }
}