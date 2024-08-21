from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from django.contrib.auth import get_user_model


from posts.models import Comment, Post, Follow, Group

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор отвечающий за группы."""

    class Meta:
        """Метаинформация для сериализатора GroupSerializer."""

        model = Group
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор отвечающий за публикации."""

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        """Метаинформация для сериализатора PostSerializer."""

        model = Post
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор отвечающий за комментарии."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        """Метаинформация для сериализатора CommentSerializer."""

        model = Comment
        fields = '__all__'
        read_only_fields = ('post',)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор отвечающий за подписки."""

    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),

    )

    class Meta:
        """Метаинформация для сериализатора FollowSerializer."""

        model = Follow
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate_following(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с указанным именем не найден'
            )
        elif self.context['request'].user == value:
            raise serializers.ValidationError(
                'Нельзя оформить подписку на себя.'
            )
        return value

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
