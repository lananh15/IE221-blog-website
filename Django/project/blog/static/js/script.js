let navbar = document.querySelector('.header .flex .navbar');

document.querySelector('#menu-btn').onclick = () =>{
   navbar.classList.toggle('active');
   searchForm.classList.remove('active');
   profile.classList.remove('active');
}

let profile = document.querySelector('.header .flex .profile');

document.querySelector('#user-btn').onclick = () =>{
   profile.classList.toggle('active');
   searchForm.classList.remove('active');
   navbar.classList.remove('active');
}

let searchForm = document.querySelector('.header .flex .search-form');

document.querySelector('#search-btn').onclick = () =>{
   searchForm.classList.toggle('active');
   navbar.classList.remove('active');
   profile.classList.remove('active');
}

window.onscroll = () =>{
   profile.classList.remove('active');
   navbar.classList.remove('active');
   searchForm.classList.remove('active');
}

document.querySelectorAll('.content-150').forEach(content => {
   if(content.innerHTML.length > 150) content.innerHTML = content.innerHTML.slice(0, 150);
});


$(document).ready(function () {
   $(".like-btn").click(function (e) {
      e.preventDefault();  // Ngăn chặn submit form mặc định

      let postId = $(this).data("post-id");
      let likeIcon = $(this).find("i");
      let likeCountSpan = $(this).find(".like-count");

      $.ajax({
         url: `/like-post/${postId}`,
         type: "POST",
         headers: { "X-CSRFToken": getCSRFToken() },
         success: function (data) {
            if (data.liked) {
               likeIcon.css("color", "red");
            } else {
               likeIcon.css("color", "");
            }
            likeCountSpan.text(`(${data.total_likes})`);
         },
         error: function (xhr, status, error) {
            console.error("Lỗi khi xử lý like:", error);
         }
      });
   });
});

// Hàm lấy CSRF token
function getCSRFToken() {
   return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}
