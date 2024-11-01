<?php

include 'components/connect.php';

session_start();

if(isset($_SESSION['user_id'])){
   $user_id = $_SESSION['user_id'];
}else{
   $user_id = '';
};

include 'components/like_post.php';

?>
<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <meta http-equiv="X-UA-Compatible" content="IE=edge">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>Contact</title>

   <!-- font awesome cdn link  -->
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
   <link rel="icon" type="image/x-icon" href="uploaded_img/doraemon.webp">
   <!-- custom css file link  -->
   <link rel="stylesheet" href="css/style.css">

</head>
<body>
   
<!-- header section starts  -->
<?php include 'components/user_header.php'; ?>
<!-- header section ends -->


<section class="simple-content">

   <h1 class="heading">Get in Touch with PyBlog Team 🤝</h1>
   <div class="box-container">
      <div class="box">
         <h2>Main Office</h2>
         <p>
            Ho Chi Minh City, Vietnam<br>
            Working Hours: Monday - Friday, 9:00 AM - 6:00 PM (GMT+7)
         </p>
         <h2>Connect With Us 🔗</h2>
         <p> Email:
            <a href="mailto:insideoutwebsitevn@gmail.com">insideoutwebsitevn@gmail.com</a> 😁
            <br>Response Time: Within 24-48 hours
         </p>
         <p> Facebook:  
            <a href="https://www.facebook.com/lananh15112004">Lan Anh</a> 👻
         </p>
         <h2>Write for PyBlog ✍️</h2>
         <p>
            Are you passionate about development and want to share your knowledge? We're always looking for guest writers! Email us at the email above.
         </p>
      </div>
   </div>
      
</section>


<?php include 'components/footer.php'; ?>

<!-- custom js file link  -->
<script src="js/script.js"></script>

</body>
</html>