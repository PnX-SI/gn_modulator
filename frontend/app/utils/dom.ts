export default {
  waitForElement: (id, container: any = document) => {
    let cpt = 100;
    return new Promise((resolve, reject) => {
      const checkExist = setInterval(function () {
        if (!container) {
          reject(null);
          return;
        }
        const elem = container.getElementById
          ? container.getElementById(id)
          : container.querySelector(`#${id}`);
        if (cpt > 500) {
          clearInterval(checkExist);
          return;
        }

        if (elem) {
          resolve(elem as HTMLElement);
          clearInterval(checkExist);
          return;
        }
        cpt += 1;
      }, 100);
    });
  },
  waitForElements: (selector, container: any = document) => {
    return new Promise((resolve, reject) => {
      const checkExist = setInterval(function () {
        const elems = container.querySelectorAll(selector);
        if (elems) {
          resolve(elems as Array<any>);
          clearInterval(checkExist);
          return;
        }
      }, 100);
    });
  },
};
