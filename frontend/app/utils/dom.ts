export default {
  waitForElement: (id, container: any =document) => {
    return new Promise((resolve, reject) => {
      const checkExist = setInterval(function() {
        const elem = container.getElementById(id);
        if (elem) {
          resolve(elem)
          clearInterval(checkExist);
          return;
        }
     }, 100);
    });
  },
  waitForElements: (selector, container: any = document) => {
    return new Promise((resolve, reject) => {
      const checkExist = setInterval(function() {
        const elems = container.querySelectorAll(selector);
        if (elems) {
          resolve(elems as Array<any>)
          clearInterval(checkExist);
          return;
        }
     }, 100);
    });
  }

}