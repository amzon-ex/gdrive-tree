$(function () {
      $('.tree li:has(ul)').addClass('parent_li').find(' > div').attr('title', 'Collapse this folder');
      $('.tree li.parent_li > div').on('click', function (e) {
          var children = $(this).parent('li.parent_li').find(' > ul > li');
          if (children.is(":visible")) {
              children.hide('fast');
              $(this).attr('title', 'Expand this folder').find(' > span > i').addClass('fa-folder').removeClass('fa-folder-open');
          } else {
              children.show('fast');
              $(this).attr('title', 'Collapse this folder').find(' > span > i').addClass('fa-folder-open').removeClass('fa-folder');
          }
          e.stopPropagation();
      });
  });