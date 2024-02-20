       const script = document.createElement("script");
      script.src = "https://secure.nmi.com/js/v1/Gateway.js";
      script.async = true;

      document.body.appendChild(script);

      script.onload = () => {
        const gateway = window.Gateway.create(
          "checkout_public_4xa72wwg38MQUH5be88gHE24nFBZern4"
        );
        const threeDS = gateway.get3DSecure();
        const options = {
          cardNumber: "4000000000002503",
            cardExpMonth: "01",
            cardExpYear: "2024",
            currency: 'USD',
            amount: '10.00',
            email: 'none@example.com',
            phone: '8008675309',
            city: 'New York',
            state: 'NY',
            address1: '123 First St.',
            country: 'US',
            firstName: 'Jane',
            lastName: 'Doe',
            postalCode: '60001'
        };
        const threeDSecureInterface = threeDS.createUI(options);
        threeDSecureInterface.start("body");
        threeDSecureInterface.on("challenge", function (e) {
          console.log("Challenged");
          alert("Challenged");
        });
        // threeDSecureInterface.on("complete", function (e) {
        //   axios
        //     .post("https://charge.ideologicstech.com/payment", {
        //       ...options,
        //       cavv: e.cavv,
        //       xid: e.xid,
        //       eci: e.eci,
        //       cardHolderAuth: e.cardHolderAuth,
        //       threeDsVersion: e.threeDsVersion,
        //       directoryServerId: e.directoryServerId,
        //       cardHolderInfo: e.cardHolderInfo,
        //     })
        //     .then((res) => {
        //       setLoader(true);
        //       console.log(res?.data);
        //       if (res?.data?.status === 200) {
        //         alert(
        //           `Transaction Successfull with id : ${res?.data?.data?.transactionid}`
        //         );
        //         setLoader(false);
        //       } else {
        //         alert(
        //           `Code: ${res?.data?.data?.response_code} ${res?.data?.data?.responsetext}`
        //         );
        //         setLoader(false);
        //         setShowModal(false);
        //       }
        //     })
        //     .catch((error) => {
        //       if (error?.response?.status === 400) {
        //         alert("Invalid Card Number. Please enter a valid card number.");
        //       } else {
        //         alert(
        //           "Transaction Failed. Try again with a different Card Number."
        //         );
        //       }
        //     });
        // });
        threeDSecureInterface.on("failure", function (e) {
          alert("Transaction Failed. Try again with different Card Number");
          console.log("failure");
          console.log(e);
        });
        threeDSecureInterface.on("error", function (e) {
          alert("Transaction Failed. Try again with different Card Number");
          console.log("error");
          console.log(e);
        });
        gateway.on("error", function (e) {
          alert("Try Again");
          console.error(e);
        });
      };
        // console.log("asad")
        // function getCookie(name) {
        //     const value = `; ${document.cookie}`;
        //     const parts = value.split(`; ${name}=`);
        //     if (parts.length === 2) return parts.pop().split(';').shift();
        // }
        //
        // const csrftoken = getCookie('csrftoken');
        // const gateway = window.Gateway.create('checkout_public_4xa72wwg38MQUH5be88gHE24nFBZern4');
        //
        // // Initialize the ThreeDSService
        // const threeDS = gateway.get3DSecure();
        //
        // const options = {
        //     cardNumber: "4000000000002503",
        //     cardExpMonth: "01",
        //     cardExpYear: "2024",
        //     currency: 'USD',
        //     amount: '10.00',
        //     email: 'none@example.com',
        //     phone: '8008675309',
        //     city: 'New York',
        //     state: 'NY',
        //     address1: '123 First St.',
        //     country: 'US',
        //     firstName: 'Jane',
        //     lastName: 'Doe',
        //     postalCode: '60001'
        // };
        //
        // const threeDSecureInterface = threeDS.createUI(options);
        //
        // threeDSecureInterface.start('body');
        //
        // threeDSecureInterface.on('challenge', function (e) {
        //    alert('Challenged');
        // });
        //
        // document.getElementById('checkoutButton').addEventListener('click', function () {
        //     threeDSecureInterface.complete();
        // });
        //
        // threeDSecureInterface.on('complete', function (e) {
        //     document.getElementById('result').innerText = JSON.stringify(e);
        //     fetch('/test/', {
        //         method: 'GET',
        //         headers: {
        //             'Content-Type': 'application/json',
        //             'X-CSRFToken': csrftoken,
        //         },
        //         body: JSON.stringify({
        //             ...options,
        //             cavv: e.cavv,
        //             xid: e.xid,
        //             eci: e.eci,
        //             cardHolderAuth: e.cardHolderAuth,
        //             threeDsVersion: e.threeDsVersion,
        //             directoryServerId: e.directoryServerId,
        //             cardHolderInfo: e.cardHolderInfo,
        //         })
        //     }).then(response => {
        //         if (!response.ok) {
        //             throw new Error('Network response was not ok');
        //         }
        //         return response.json();
        //     }).then(data => {
        //         console.log(data);
        //     }).catch(error => {
        //         console.error('Error during fetch:', error);
        //     });
        // });
        //
        // threeDSecureInterface.on('failure', function (e) {
        //     console.log('failure');
        //     console.log(e);
        // });
        //
        // // Listen for any errors that might occur.
        // gateway.on('error', function (e) {
        //     console.error(e);
        // });