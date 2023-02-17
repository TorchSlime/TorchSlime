"""
Status Pattern for model status management.
"""
from torchslime.util import NOTHING, is_nothing
from torchslime.module import Registry
from torchslime.core.context import BaseContext

context_status = Registry('context_status')


class Status:

    def __init__(self) -> None:
        pass

    def set_model_mode(self, ctx: BaseContext):
        pass

    def get_dataset(self, ctx: BaseContext):
        pass

    def get_avg_loss_and_metrics(self, ctx: BaseContext):
        pass

    def init_avg_inner_ctx(self, ctx: BaseContext, INNER_KEY):
        if is_nothing(ctx.inner[INNER_KEY]):
            ctx.inner[INNER_KEY] = {}

    def set_avg_loss_and_metrics(self, ctx: BaseContext, loss, metrics):
        pass

    def get_avg_inner_ctx(self, ctx: BaseContext, INNER_KEY):
        pass

    def clear_avg_info(self, ctx: BaseContext, INNER_KEY):
        if is_nothing(ctx.inner[INNER_KEY]):
            ctx.inner[INNER_KEY] = {}

    def _get_avg_inner_init_item(self, ctx: BaseContext):
        return {
            'loss_value': ctx.run.loss_wrapper.get_empty(),
            'loss_value_count': {},
            'metrics': {},
            'metrics_count': {}
        }

    def __str__(self) -> str:
        return 'BASE STATUS'


@context_status.register('train')
class TrainStatus(Status):

    def __init__(self) -> None:
        super().__init__()

    def set_model_mode(self, ctx: BaseContext):
        ctx.model.train()

    def get_dataset(self, ctx: BaseContext):
        ctx.ctx_check('run.train_provider', silent=False)
        ctx.dataset = ctx.run.train_provider(ctx)

    def get_avg_loss_and_metrics(self, ctx: BaseContext) -> list:
        # TODO: loss dict
        data = []
        if is_nothing(ctx.epoch.train_loss_value) is False:
            data.append('loss: {0:.5f}'.format(ctx.epoch.train_loss_value))
        for key, value in ctx.epoch.train_metrics.items():
            data.append('{0}: {1:.5f}'.format(key, value))
        return data
    
    def init_avg_inner_ctx(self, ctx: BaseContext, INNER_KEY):
        super().init_avg_inner_ctx(ctx, INNER_KEY)
        if is_nothing(ctx.inner[INNER_KEY].get('train', NOTHING)):
            ctx.inner[INNER_KEY]['train'] = self._get_avg_inner_init_item(ctx)
    
    def set_avg_loss_and_metrics(self, ctx: BaseContext, loss, metrics):
        ctx.epoch.train_loss_value = loss
        ctx.epoch.train_metrics = metrics

    def get_avg_inner_ctx(self, ctx: BaseContext, INNER_KEY):
        return ctx.inner[INNER_KEY].get('train', NOTHING)

    def clear_avg_info(self, ctx: BaseContext, INNER_KEY):
        super().clear_avg_info(ctx, INNER_KEY)
        ctx.inner[INNER_KEY]['train'] = self._get_avg_inner_init_item(ctx)
        ctx.epoch.train_metrics = NOTHING
        ctx.epoch.train_loss_value = NOTHING

    def __str__(self) -> str:
        return 'TRAIN'


@context_status.register('eval')
class EvalStatus(Status):

    def __init__(self) -> None:
        super().__init__()
    
    def set_model_mode(self, ctx: BaseContext):
        ctx.model.eval()

    def get_dataset(self, ctx: BaseContext):
        ctx.ctx_check('run.eval_provider', silent=False)
        ctx.dataset = ctx.run.eval_provider(ctx)

    def get_avg_loss_and_metrics(self, ctx: BaseContext):
        data = []
        if is_nothing(ctx.epoch.eval_loss_value) is False:
            data.append('loss: {0:.5f}'.format(ctx.epoch.eval_loss_value))
        for key, value in ctx.epoch.eval_metrics.items():
            data.append('{0}: {1:.5f}'.format(key, value))
        return data

    def init_avg_inner_ctx(self, ctx: BaseContext, INNER_KEY):
        super().init_avg_inner_ctx(ctx, INNER_KEY)
        if is_nothing(ctx.inner[INNER_KEY].get('eval', NOTHING)):
            ctx.inner[INNER_KEY]['eval'] = self._get_avg_inner_init_item(ctx)

    def set_avg_loss_and_metrics(self, ctx: BaseContext, loss, metrics):
        ctx.epoch.eval_loss_value = loss
        ctx.epoch.eval_metrics = metrics
    
    def get_avg_inner_ctx(self, ctx: BaseContext, INNER_KEY):
        return ctx.inner[INNER_KEY].get('eval', NOTHING)

    def clear_avg_info(self, ctx: BaseContext, INNER_KEY):
        super().clear_avg_info(ctx, INNER_KEY)
        ctx.inner[INNER_KEY]['eval'] = self._get_avg_inner_init_item(ctx)
        ctx.epoch.eval_metrics = NOTHING
        ctx.epoch.eval_loss_value = NOTHING

    def __str__(self) -> str:
        return 'EVAL'


@context_status.register('val')
class ValStatus(EvalStatus):

    def __init__(self) -> None:
        super().__init__()

    def set_avg_loss_and_metrics(self, ctx: BaseContext, loss, metrics):
        ctx.epoch.eval_loss_value = loss
        _metrics = {}
        for key, value in metrics.items():
            _metrics['val_{0}'.format(key)] = value
        ctx.epoch.eval_metrics = _metrics

    def get_avg_loss_and_metrics(self, ctx: BaseContext):
        data = []
        if is_nothing(ctx.epoch.eval_loss_value) is False:
            data.append('val_loss: {0:.5f}'.format(ctx.epoch.eval_loss_value))
        for key, value in ctx.epoch.eval_metrics.items():
            data.append('{0}: {1:.5f}'.format(key, value))
        return data

    def __str__(self) -> str:
        return 'VAL'


@context_status.register('predict')
class PredictStatus(EvalStatus):

    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return 'PREDICT'
