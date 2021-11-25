from django.core.mail import EmailMessage


def sendemail(request,mode):
    if mode == 'follow': # requset는 팔로우 한 유저, 팔로우 당한 사람에게 이메일 전송
        follower = request[1]
        person = request[0]

        email = EmailMessage(
        f'[MovieGram] {person.nickname}이 {follower.nickname}을 팔로우 하기 시작했습니다',                # 제목
        '지금 바로 무비그램에서 만나보세요!',       # 내용
        to=[f'{follower.email}'],  # 받는 이메일 리스트
    )
    elif mode=='newreview':
        to_list =[]
        nickname=request['user'].nickname
        moviename = request['review'].movie.title
        title = request['review'].title
        content = request['review'].content
        rank = request['review'].rank
        for follower in request['user'].followers.all():
             to_list.append(follower.email)
        email = EmailMessage(
        f'[MovieGram] {nickname}님께서 새로운 영화 리뷰를 작성했습니다',                # 제목
        f"""{moviename}에 대한 {nickname}님의 새로운 리뷰
        제목 : {title} 평점:{rank}
        내용 : {content}
        """,       # 내용
        to=to_list,  # 받는 이메일 리스트
    )
    elif mode == 'like':
        review_user = request['review'].user.nickname
        review_movie = request['review'].movie.title
        review_title = request['review'].title
        like_user = request['like_user'].nickname

        email = EmailMessage( f'[MovieGram] {like_user}님께서 {review_user}의 리뷰를 좋아합니다',
         f"""{like_user}님께서 {review_user}의 {review_movie} 리뷰를 좋아합니다.
         리뷰제목:{review_title} 
         """,       # 내용
        to=[request['review'].user.email],  # 받는 이메일 리스트
    )
    elif mode == 'comment':
        review_user = request['review'].user.nickname
        review_movie = request['review'].movie.title
        review_title = request['review'].title
        comment_user = request['comment'].user.nickname
        comment_content = request['comment'].content
        email = EmailMessage(
        f'[MovieGram] {review_user}님의 리뷰에 댓글이 달렸습니다',                # 제목
        f"""{comment_user}님께서 {review_user}이 
        {review_movie}에 남기신 리뷰 "{review_title}"에 댓글을 남겼습니다
        댓글: {comment_content}""",       # 내용
        to=[request['review'].user.email],  # 받는 이메일 리스트
    )
   
    email.send()
    